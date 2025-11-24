"""
Module for models related to political statements.
"""

from pydantic import BaseModel
from typing import Dict, Any, List


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