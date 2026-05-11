"""
chunking data models
"""
import json
import uuid

from pydantic import BaseModel
from typing import List, Any, Dict


class Chunk(BaseModel):
    """
    Document chunk model
    """
    id: uuid.UUID
    doc_name: str
    party: str
    page_number: int
    year: int
    content: str
    dense_vector: List[float]
    summary: str
    metadata: Dict[str, Any]

    async def to_milvus_dict(self) -> Dict:
        """convert chunk to a flat dict ready for Milvus insert (metadata serialized to JSON string)."""
        milvus_dict = {
            "id": str(self.id),
            "doc_name": self.doc_name,
            "party": self.party,
            "page_number": self.page_number,
            "year": self.year,
            "content": self.content,
            "dense_vector": self.dense_vector,
            "metadata": json.dumps(self.metadata)  # must format to str for Milvus
        }

        return milvus_dict