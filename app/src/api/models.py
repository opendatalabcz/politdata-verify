"""
api models package
"""
import re
import uuid
from pydantic import BaseModel, field_validator
from typing import List, Literal, Union

from app.src.political_statements.models import ClassifiedStatement, Speaker, StatsResult

_COLLECTION_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,254}$')

def _validate_collection_name(v: str) -> str:
    if not _COLLECTION_NAME_RE.match(v):
        raise ValueError(
            "Název kolekce smí obsahovat pouze písmena, číslice a podtržítka, "
            "musí začínat písmenem nebo podtržítkem a mít nejvýše 255 znaků."
        )
    return v

class VerifyStatementsPayload(BaseModel):
    """
    Model representing a political statement verification request.
    """
    text: str
    speaker_list: List[Speaker] | None = None
    collection_name: str = "test_collection"
    year: int = 2025
    mode: Literal["sync", "async"] = "async"

    _validate_col = field_validator("collection_name")(_validate_collection_name)


class Statement(BaseModel):
    """
    Model representing a political statement.
    """
    query: str
    collection_name: str
    party: str | None = None
    year: int | None = None

    _validate_col = field_validator("collection_name")(_validate_collection_name)

class StatementsPayload(BaseModel):
    """
    Model representing a collection of political statements.
    """
    statements: List[Statement]

class Document(BaseModel):
    """
    Model representing a document.
    """
    url: str
    name: str
    collection_name: str
    party: str | None = None
    year: int | None = None

    _validate_col = field_validator("collection_name")(_validate_collection_name)

    def model_post_init(self, __context):
        if not self.url.startswith("https://"):
            raise ValueError("Document URL must use HTTPS")

class DocumentPayload(BaseModel):
    """
    Model representing a collection of documents.
    """
    documents: List[Document]


class JobRequest(BaseModel):
    """
    Payload model for classify statement job.
    """
    job_id: uuid.UUID
    payload: Union[StatementsPayload, DocumentPayload, VerifyStatementsPayload]

class ClassifyStatementJobResponse(BaseModel):
    """
    Response model for classify statement job.
    """
    type: Literal["STATEMENT_CLASSIFICATION"] = "STATEMENT_CLASSIFICATION"
    classified_statements: List[ClassifiedStatement]

class VerifyPoliticalStatementsJobResponse(BaseModel):
    """
    Response model for verify political statements job.
    """
    type: Literal["VERIFY_POLITICAL_STATEMENTS"] = "VERIFY_POLITICAL_STATEMENTS"
    stats: StatsResult


