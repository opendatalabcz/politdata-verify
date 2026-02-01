import logging
from fastapi import FastAPI

from app.src.api.jobs import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Political RAG API")

app.include_router(router, prefix="/api/v1/jobs", tags=["jobs"])

@app.get("/health")
async def health_check():
    logger.info("Health check")
    return {"status": "running"}