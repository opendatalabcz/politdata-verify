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

class ClassifiedStatementWithContext(ClassifiedStatement):
    """
    Model representing a classified political statement with additional context.
    """
    speaker: str
    party: str
    statement: str

class SpeakerStats(BaseModel):
    speaker: str
    party: str
    total_statements: int
    supported: List[ClassifiedStatementWithContext]
    contradicted: List[ClassifiedStatementWithContext]
    insufficient: List[ClassifiedStatementWithContext]

class StatsResult(BaseModel):
    total_speakers: int
    total_statements: int
    speakers_stats: List[SpeakerStats]