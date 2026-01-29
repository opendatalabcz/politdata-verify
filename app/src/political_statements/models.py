"""
Module for models related to political statements.
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Literal

class Statement(BaseModel):
    """
    Model representing a political statement.
    """
    text: str
    metadata: Dict[str, Any]

class Statements(BaseModel):
    """
    Model representing a collection of political statements.
    """
    statements: List[Statement]

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