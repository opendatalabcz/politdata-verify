"""
milvus interface
"""
import asyncio
import os
from typing import List, Dict, Any

from pymilvus import AsyncMilvusClient, MilvusClient, AnnSearchRequest, WeightedRanker

from app.src.chunking.models import Chunk
from app.src.embeddings.jina_client import JinaEmbedder
from app.src.milvus.schema import create_schema
import logging

logger = logging.getLogger(__name__)

URL = os.getenv("MILVUS_URI", "http://milvus-standalone:19530")
# URL = "http://localhost:19530"
RETRIEVAL_TOP_K = 20
RERANKER_DENSE_FACTOR = 0.4
RERANKER_SPARSE_FACTOR = 0.6
MILVUS_MAX_INSERT_BATCH_SIZE = 1000

class MilvusInterface:
    def __init__(self):
        """contains config"""

        self.uri = URL
        self.async_client = AsyncMilvusClient(uri=self.uri)
        self.client = MilvusClient(uri=self.uri)

    async def close(self):
        await self.async_client.close()

    async def create_collection(self, collection_name: str) -> None:
        """
        create milvus collection
        """
        if self.has_collection(collection_name):
            return

        # create schema
        schema = create_schema(collection_name)

        # init index params
        index_params = self.client.prepare_index_params()

        # dense vector index
        index_params.add_index(
            field_name='dense_vector',
            metric_type='COSINE',
            index_type='HNSW',
            index_name='dense_vector_index',
            params={
                "M": 32,
                "efConstruction": 200
            }
        )

        # sparse vector index
        index_params.add_index(
            field_name='sparse_vector',
            metric_type='BM25',
            index_type='SPARSE_INVERTED_INDEX',
            index_name='sparse_vector_index',
            params={
                "inverted_index_algo": "DAAT_MAXSCORE",
                "bm25_k1": 1.2,
                "bm25_b": 0.75
            }
        )

        # create collection
        await self.async_client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params,
        )
        print(f"[MILVUS] Created collection {collection_name}")

    async def insert_chunks(self, collection_name: str, chunks: List[Chunk]) -> None:
        """
        insert chunks into milvus collection
        collection_name: milvus collection name
        entities: list of chunk dicts
        """
        if not self.has_collection(collection_name):
            print(f"Collection {collection_name} does not exist. Creating collection...")
            await self.create_collection(collection_name)

        # convert chunks to dicts
        chunk_dicts = [await chunk.to_milvus_dict() for chunk in chunks]
        chunk_dicts_batches = await self.create_chunk_batches_for_insert(chunk_dicts)
        insert_tasks = [self.async_client.insert(collection_name, batch) for batch in chunk_dicts_batches]

        await asyncio.gather(*insert_tasks)

        # flush
        self.client.flush(collection_name)

        # release
        await self.async_client.release_collection(collection_name)

        print(f"[MILVUS] Added {len(chunks)} chunks to collection {collection_name}")

    async def delete_chunks_by_party(self, collection_name: str, party_name) -> int:
        """
        delete chunks from milvus collection
        collection_name: milvus collection name
        party_name: party name to delete
        return: number of deleted chunks
        """
        if not self.has_collection(collection_name):
            logger.warning(f"Collection {collection_name} does not exist.")
            return 0

        await self.async_client.load_collection(collection_name)

        expr = f"party == '{party_name}'"

        try:
            chunks_count = self.client.query(collection_name=collection_name, filter=expr, output_fields=["count(*)"])
            deleted_chunks = chunks_count[0]['count(*)']
            await self.async_client.delete(collection_name, filter=expr)
            logger.info(f"[MILVUS] Found and deleting {chunks_count[0]['count(*)']} chunks with party '{party_name}' from collection {collection_name}")
        except Exception as e:
            logger.error(f"[MILVUS] Error deleting chunks with party '{party_name}' from collection {collection_name}: {e}")
            return 0

        # release
        await self.async_client.release_collection(collection_name)
        return deleted_chunks

    async def get_number_of_chunks_by_party(self, collection_name: str, party: str) -> int:
        """
        get number of chunks in milvus collection
        collection_name: milvus collection name
        party: party name to filter
        return: number of chunks
        """
        if not self.has_collection(collection_name):
            logger.warning(f"Collection {collection_name} does not exist.")
            return 0

        await self.async_client.load_collection(collection_name)

        expr = f"party == '{party}'"
        chunks_count = self.client.query(collection_name=collection_name, filter=expr, output_fields=["count(*)"])

        await self.async_client.release_collection(collection_name)
        return chunks_count[0]['count(*)']




    async def list_collections_with_stats(self) -> list[dict]:
        collections = self.client.list_collections()
        result = []
        for col in collections:
            try:
                await self.async_client.load_collection(col)
                rows = self.client.query(collection_name=col, filter="", output_fields=["party", "doc_name"], limit=16384)
                parties = list({r["party"] for r in rows if r.get("party")})
                party_stats = []
                for party in sorted(parties):
                    count_rows = self.client.query(
                        collection_name=col,
                        filter=f"party == '{party}'",
                        output_fields=["count(*)"],
                    )
                    name_rows = self.client.query(
                        collection_name=col,
                        filter=f"party == '{party}'",
                        output_fields=["doc_name", "content"],
                        limit=16384,
                    )
                    doc_names = list({r["doc_name"] for r in name_rows if r.get("doc_name")})
                    total_chars = sum(len(r.get("content", "")) for r in name_rows)
                    party_stats.append({"party": party, "chunk_count": count_rows[0]["count(*)"], "doc_names": doc_names, "total_chars": total_chars})
                await self.async_client.release_collection(col)
                result.append({"collection_name": col, "parties": party_stats})
            except Exception as e:
                logger.warning(f"[LIST_COLLECTIONS] Error processing {col}: {e}")
                result.append({"collection_name": col, "parties": []})
        return result

    async def drop_collection(self, collection_name: str) -> None:
        """
        delete milvus collection
        """
        if not self.has_collection(collection_name):
            return

        await self.async_client.drop_collection(collection_name)


    def has_collection(self, collection_name: str) -> bool:
        """
        check if milvus has collection
        """
        return self.client.has_collection(collection_name)

    async def hybrid_search(self, collection_name: str, query: str, **kwargs) -> List[List[Dict[str, Any]]] | None:
        """
        perform hybrid search on milvus collection
        collection_name: milvus collection name
        query: search query
        return: list of relevant chunks
        """
        if not self.has_collection(collection_name):
            print(f"Collection {collection_name} does not exist.")
            return

        await self.async_client.load_collection(collection_name)
        print(f"[MILVUS] {collection_name} collection loaded.")

        # building filter expression
        year = kwargs.get("year", None)
        party = kwargs.get("party", None)
        filters = []
        if party is not None:
            filters.append(f"party == '{party}'")
        if year is not None:
            filters.append(f"year == {year}")

        filter_expr = " and ".join(filters) if filters else ""

        # get query embedding
        jina_embedding_client = JinaEmbedder()
        query_embedding = await jina_embedding_client.get_embedding(
            text={"text": query},
            task="retrieval.query"
        )

        # --- DENSE (HNSW) ---
        dense_search_params = {
            "data": [query_embedding],
            "anns_field": "dense_vector",
            "param": {
                "metric_type": "COSINE",
                "params": {"ef": 4 * RETRIEVAL_TOP_K}
            },
            "expr": filter_expr,
            "limit": RETRIEVAL_TOP_K
        }

        # --- SPARSE (BM25) ---
        sparse_search_params = {
            "data": [query],
            "anns_field": "sparse_vector",
            "param": {
                "params": {"drop_ratio_search": 0.2}
            },
            "expr": filter_expr,
            "limit": RETRIEVAL_TOP_K
        }

        # --- HYBRID ---
        reqs = [AnnSearchRequest(**dense_search_params),
                AnnSearchRequest(**sparse_search_params)]

        ranker = WeightedRanker(RERANKER_DENSE_FACTOR,
                                RERANKER_SPARSE_FACTOR)

        result = await self.async_client.hybrid_search(
            collection_name=collection_name,
            reqs=reqs,
            ranker=ranker,
            limit=RETRIEVAL_TOP_K,
            output_fields=['id', 'doc_name', 'party', 'page_number', 'year', 'content', 'metadata']
        )

        return result

    @staticmethod
    async def create_chunk_batches_for_insert(chunk_dicts: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Prevent too large insert error
        """
        n = MILVUS_MAX_INSERT_BATCH_SIZE
        return [chunk_dicts[i: i + n] for i in range(0, len(chunk_dicts), n)]


if __name__ == "__main__":
    async def main():
        interface = MilvusInterface()
        await interface.create_collection("test_collection")

    asyncio.run(main())
