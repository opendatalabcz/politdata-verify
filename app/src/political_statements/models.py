"""
Module for models related to political statements.
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Literal

class Speaker(BaseModel):
    name: str
    party: str | None = None

class Speakers(BaseModel):
    speakers: List[Speaker]

class Statement(BaseModel):
    statement: str
    original_quote: str
    confidence: float

class SpeakerStatements(BaseModel):
    speaker: Speaker
    statements: List[Statement]

class ExtractionResult(BaseModel):
    speakers: List[SpeakerStatements]

CLASSIFICATION = Literal["SUPPORTED", "CONTRADICTED", "INSUFFICIENT"]

class Evidence(BaseModel):
    """
    Model representing evidence for statement classification.
    """
    quote: str
    citation: str

class ClassifiedStatement(BaseModel):
    """
    Model representing a classified political statement.
    """
    verdict: CLASSIFICATION
    rationale: str
    evidence: List[Evidence]
    confidence: float