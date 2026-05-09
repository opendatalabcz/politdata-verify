"""
api models package
"""
import uuid
from pydantic import BaseModel
from typing import List, Literal, Union

from app.src.political_statements.models import ClassifiedStatement, Speaker, StatsResult

class VerifyStatementsPayload(BaseModel):
    """
    Model representing a political statement verification request.
    """
    text: str
    speaker_list: List[Speaker] | None = None
    collection_name: str = "test_collection"
    year: int = 2025
    mode: Literal["sync", "async"] = "async"


class Statement(BaseModel):
    """
    Model representing a political statement.
    """
    query: str
    collection_name: str
    party: str | None = None
    year: int | None = None

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


