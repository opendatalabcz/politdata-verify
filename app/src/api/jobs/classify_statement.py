"""
classify statements API job
"""
import logging
import uuid
from typing import List

from app.src.api import job_store
from app.src.api.models import Statement, ClassifyStatementJobResponse, StatementsPayload
from app.src.clients.openai_client import Client
from app.src.political_statements.models import ClassifiedStatement
from app.src.political_statements.statement_classification import classify_statement

logger = logging.getLogger(__name__)


async def classify_statement_job(job_id: uuid.UUID, payload: dict):
    job_store.set_pending(str(job_id))
    try:
        client = Client()
        statements: List[Statement] = [Statement(**s) for s in payload["statements"]]
        results: List[ClassifiedStatement] = []
        for statement in statements:
            classification = await classify_statement(
                query=statement.query,
                collection_name=statement.collection_name,
                client=client,
                party=statement.party,
                year=statement.year,
            )
            results.append(classification)
        response = ClassifyStatementJobResponse(classified_statements=results)
        job_store.set_completed(str(job_id), response.model_dump(mode="json"))
        logger.info(f"[STATEMENT_CLASSIFICATION] Job {job_id} completed with {len(results)} statements.")
    except Exception as exc:
        logger.exception(f"[CLASSIFICATION_FAILED] Job {job_id}: {exc}")
        job_store.set_failed(str(job_id), str(exc))
