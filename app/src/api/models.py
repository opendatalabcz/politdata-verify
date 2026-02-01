"""
api models package
"""
import uuid
from pydantic import BaseModel
from typing import List, Literal, Union

from app.src.political_statements.models import ClassifiedStatement


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

class JobRequest(BaseModel):
    """
    Payload model for classify statement job.
    """
    job_id: uuid.UUID
    payload: Union[StatementsPayload]

class ClassifyStatementJobResponse(BaseModel):
    """
    Response model for classify statement job.
    """
    type: Literal["STATEMENT_CLASSIFICATION"] = "STATEMENT_CLASSIFICATION"
    classified_statements: List[ClassifiedStatement]


