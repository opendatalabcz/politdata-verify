from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from app.src.api.models import *
from app.src.api.auth import verify_api_key
from app.src.api.admin_auth import verify_admin_token
from app.src.api.rate_limiter import check_rate_limit, MAX_QUERY_CHARS
from app.src.api import job_store

from app.src.chunking.pdf_chunker import pdf_chunker
from app.src.milvus.milvus_interface import MilvusInterface
from app.src.political_statements.statement_classification import classify_statement

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.post("/classify_statements")
async def run_classify_statements_job(
    request: JobRequest,
    background_tasks: BackgroundTasks,
    http_request: Request
):
    """
    Endpoint to start a classify statements job.
    """
    from app.src.api.jobs.classify_statement import classify_statement_job

    job_id = request.job_id
    payload = request.payload
    for s in payload.statements:
        if len(s.query) > MAX_QUERY_CHARS:
            raise HTTPException(status_code=400, detail=f"Výrok je příliš dlouhý. Maximum je {MAX_QUERY_CHARS} znaků.")
    combined_text = " ".join(s.query for s in payload.statements)
    check_rate_limit(http_request, combined_text)
    job_store.set_pending(str(job_id))
    background_tasks.add_task(classify_statement_job, job_id, payload.model_dump())

    return {"status": "Classify statements job has been started", "job_id": str(job_id)}

@router.post("/add_document", dependencies=[Depends(verify_admin_token)])
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
    job_store.set_pending(str(job_id))
    background_tasks.add_task(add_document_job, job_id, payload.model_dump())

    return {"status": "Add document job has been started", "job_id": str(job_id)}

@router.post("/verify_political_statements")
async def verify_political_statements(request: JobRequest, background_tasks: BackgroundTasks, http_request: Request):
    """
    Endpoint to start a verify political statements job.
    """
    from app.src.api.jobs.verify_political_statements import verify_political_statements_job

    job_id = request.job_id
    payload = request.payload
    check_rate_limit(http_request, payload.text)
    job_store.set_pending(str(job_id))
    background_tasks.add_task(verify_political_statements_job, job_id, payload)

    return {"status": "Verify political statements job has been started", "job_id": str(job_id)}


@router.get("/result/{job_id}")
async def get_job_result(job_id: str):
    """
    Poll the result of a background job by its ID.
    Returns status PENDING | COMPLETED | FAILED, and result when completed.
    """
    entry = job_store.get_job(job_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(content=entry)