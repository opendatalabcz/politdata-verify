"""
background job wrapper for the verify_political_statements pipeline.
"""
import logging
import uuid

from app.src.api import job_store
from app.src.api.models import VerifyStatementsPayload
from app.src.political_statements.job import verify_political_statements

logger = logging.getLogger(__name__)


async def verify_political_statements_job(job_id: uuid.UUID, payload: VerifyStatementsPayload):
    """run the full extraction + classification pipeline and store the StatsResult in job_store."""
    job_store.set_pending(str(job_id))
    try:
        result = await verify_political_statements(
            text=payload.text,
            speakers_list=payload.speaker_list,
            collection_name=payload.collection_name,
            year=payload.year,
            mode=payload.mode
        )
        job_store.set_completed(str(job_id), result.model_dump(mode="json"))
        logger.info(f"\033[35m[JOB_COMPLETED] Job {job_id} completed.\033[0m")
    except Exception as exc:
        logger.exception(f"[JOB_FAILED] Job {job_id} failed: {exc}")
        job_store.set_failed(str(job_id), str(exc))
