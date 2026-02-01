"""
classify statements API job
"""
import json
import logging
import uuid
from typing import List
from fastapi.responses import JSONResponse
from app.src.api.models import Statement, ClassifyStatementJobResponse, StatementsPayload
from app.src.political_statements.models import ClassifiedStatement
from app.src.political_statements.statement_classification import classify_statement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def classify_statement_job(job_id: uuid.UUID, payload: StatementsPayload):
    """
    Placeholder function for classifying statements job.
    """

    statements: List[Statement] = [Statement(**s) for s in payload["statements"]]
    results: List[ClassifiedStatement] = []
    for statement in statements:
        classification = await classify_statement(
            query=statement.query,
            collection_name=statement.collection_name,
            party=statement.party,
            year=statement.year
        )
        results.append(classification)

    response = ClassifyStatementJobResponse(classified_statements=results)

    logger.info(f"[STATEMENT_CLASSIFICATION] Job {job_id} completed with {len(results)} classified statements.")
    logger.info(f"[STATEMENT_CLASSIFICATION] Results: {json.dumps(response.model_dump(mode='json'), default=str, indent=2, ensure_ascii=False)}")

    return JSONResponse(content={"status": "STATEMENT_CLASSIFICATION has started",})


