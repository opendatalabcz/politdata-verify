"""
milvus interface
"""
from pymilvus import AsyncMilvusClient, MilvusClient

from src.milvus.schema import create_schema

URL = "http://milvus-standalone:19530"

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
        if not self.has_collection(collection_name):
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