"""
Module for models related to political statements.
"""
import logging

from pydantic import BaseModel
from typing import Dict, Any, List, Literal

logger = logging.getLogger(__name__)

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

    def pretty_print(self):
        logger.info(f"Total Speakers: {self.total_speakers}")
        logger.info(f"Total Statements: {self.total_statements}")
        for speaker_stat in self.speakers_stats:
            logger.info(f"\nSpeaker: {speaker_stat.speaker} ({speaker_stat.party})")
            logger.info(f"  Total Statements: {speaker_stat.total_statements}")
            logger.info(f"  Supported: {len(speaker_stat.supported)}")
            for s in speaker_stat.supported:
                logger.info(f"    - {s.statement} (Confidence: {s.confidence:.2f})")
            logger.info(f"  Contradicted: {len(speaker_stat.contradicted)}")
            for s in speaker_stat.contradicted:
                logger.info(f"    - {s.statement} (Confidence: {s.confidence:.2f})")
            logger.info(f"  Insufficient: {len(speaker_stat.insufficient)}")
            for s in speaker_stat.insufficient:
                logger.info(f"    - {s.statement} (Confidence: {s.confidence:.2f})")