"""
create schema
"""
import json

from pymilvus import FieldSchema, DataType, Function, FunctionType, CollectionSchema

DENSE_VECTOR_DIM = 2048
SCHEMA_VERSION = 1.0

def create_schema(collection_name: str, **kwargs) -> CollectionSchema:
    """
    Returns the Milvus collection schema
    """

    fields = [
        FieldSchema(
            name="id",
            dtype=DataType.VARCHAR,
            is_primary=True,
            auto_id=False,
            max_length=36,
            description="Externally provided id (UUID)",
        ),
        FieldSchema(
            name="doc_name",
            dtype=DataType.VARCHAR,
            description="Document name",
            max_length=255
        ),
        FieldSchema(
            name="party",
            dtype=DataType.VARCHAR,
            description="Party associated with the document chunk",
            max_length=100
        ),
        FieldSchema(
            name="page_number",
            dtype=DataType.INT32,
            description="Page number of the chunk in the original document",
        ),
        FieldSchema(
            name="year",
            dtype=DataType.INT32,
            description="Year associated with the document chunk",
        ),
        FieldSchema(
            name="content",
            dtype=DataType.VARCHAR,
            description="Chunk content",
            enable_analyzer=True,
            max_length=65535
        ),
        FieldSchema(
            name="dense_vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=DENSE_VECTOR_DIM,
            description="Dense text embedding vector",
        ),
        FieldSchema(
            name="sparse_vector",
            dtype=DataType.SPARSE_FLOAT_VECTOR,
            description="Sparse text embedding vector",
        ),
        FieldSchema(
            name="metadata",
            dtype=DataType.JSON,
            description="Metadata JSON",
        )
    ]

    functions = [
        Function(
            name="content_bm25_emb",
            input_field_names=["content"],
            output_field_names=["sparse_vector"],
            function_type=FunctionType.BM25,
        )
    ]

    metadata = kwargs.get("metadata", {})
    description = json.dumps({
        "note": f"RAG collection '{collection_name}' schema v.{SCHEMA_VERSION}",
        "metadata": metadata
    })

    return CollectionSchema(
        fields=fields,
        functions=functions,
        description=description,
    )