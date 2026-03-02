"""
classify statements API job
"""
import json
import logging
import uuid
from typing import List
from fastapi.responses import JSONResponse
from app.src.api.models import (VerifyStatementsPayload,
                                VerifyPoliticalStatementsJobResponse)
from app.src.political_statements.job import verify_political_statements
from app.src.political_statements.models import StatsResult

logger = logging.getLogger(__name__)

async def verify_political_statements_job(job_id: uuid.UUID, payload: VerifyStatementsPayload):
    """
    Placeholder function for classifying statements job.
    """
    results: List[StatsResult] = []
    result = await verify_political_statements(
        text=payload.text,
        speakers_list=payload.speaker_list,
        collection_name=payload.collection_name,
        year=payload.year
    )
    response = VerifyPoliticalStatementsJobResponse(stats=result)

    logger.info(f"[VERIFY_STATEMENTS] Job {job_id} completed with {len(results)} classified statements.")
    logger.info(f"[VERIFY_STATEMENTS] Results: {json.dumps(response.model_dump(mode='json'), default=str, indent=2, ensure_ascii=False)}")
    logger.info(f"\033[35m[JOB_COMPLETED] Job {job_id} completed.\033[0m")

    return JSONResponse(content={"status": "VERIFY_STATEMENTS has started",})


