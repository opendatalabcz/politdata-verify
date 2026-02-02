from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.src.api.models import *
from app.src.api.auth import verify_api_key

from app.src.chunking.pdf_chunker import pdf_chunker
from app.src.milvus.milvus_interface import MilvusInterface
from app.src.political_statements.statement_classification import classify_statement

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.post("/classify_statements")
async def run_classify_statements_job(
    request: JobRequest,
    background_tasks: BackgroundTasks
):
    """
    Endpoint to start a classify statements job.
    """
    from app.src.api.jobs.classify_statement import classify_statement_job

    job_id = request.job_id
    payload = request.payload
    background_tasks.add_task(classify_statement_job, job_id, payload.model_dump())

    return {"status": "Classify statements job has been started", "job_id": str(job_id)}

@router.post("/add_document")
async def run_add_document_job(
    request: JobRequest,
    background_tasks: BackgroundTasks
):
    """
    Endpoint to start an add document job.
    """
    from app.src.api.jobs.add_document import add_document_job

    job_id = request.job_id
    payload = request.payload
    background_tasks.add_task(add_document_job, job_id, payload.model_dump())

    return {"status": "Add document job has been started", "job_id": str(job_id)}