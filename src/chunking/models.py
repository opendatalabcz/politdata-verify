"""
models
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
    metadata: Dict[str, Any]

    async def to_milvus_dict(self) -> Dict:
        """
        Helper: Converts instance to dict for insertion into Milvus collection
        """
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