"""
api models package
"""
import uuid
from pydantic import BaseModel
from typing import List, Literal, Union

from app.src.political_statements.models import ClassifiedStatement
from pydantic import HttpUrl

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
    payload: Union[StatementsPayload, DocumentPayload]

class ClassifyStatementJobResponse(BaseModel):
    """
    Response model for classify statement job.
    """
    type: Literal["STATEMENT_CLASSIFICATION"] = "STATEMENT_CLASSIFICATION"
    classified_statements: List[ClassifiedStatement]


