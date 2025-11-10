"""
milvus interface
"""
import asyncio
from typing import List, Dict, Any

from pymilvus import AsyncMilvusClient, MilvusClient, AnnSearchRequest, WeightedRanker

from src.chunking.models import Chunk
from src.embeddings.jina_client import JinaEmbedder
from src.milvus.schema import create_schema

# URL = "http://milvus-standalone:19530"
URL = "http://localhost:19530"
RETRIEVAL_TOP_K = 20
RERANKER_DENSE_FACTOR = 0.6
RERANKER_SPARSE_FACTOR = 0.4
MILVUS_MAX_INSERT_BATCH_SIZE = 1000

class MilvusInterface:
    def __init__(self):
        """contains config"""

        self.uri = URL
        self.async_client = AsyncMilvusClient(uri=self.uri)
        self.client = MilvusClient(uri=self.uri)

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

    async def hybrid_search(self, collection_name: str, query: str) -> List[List[Dict[str, Any]]] | None:
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
            "limit": RETRIEVAL_TOP_K
        }

        # --- SPARSE (BM25) ---
        sparse_search_params = {
            "data": [query],
            "anns_field": "sparse_vector",
            "param": {
                "params": {"drop_ratio_search": 0.2}
            },
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
