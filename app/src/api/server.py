import logging
import uuid

from fastapi import FastAPI

from app.src.api.jobs import router
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Political RAG API")

app.include_router(router, prefix="/api/v1/jobs", tags=["jobs"])

@app.get("/health")
async def health_check():
    logger.info("Health check")
    return {"status": "running"}

@app.get("/api/v1/get_chunks/{collection_name}/{party}")
async def get_chunks(collection_name, party: str):
    """
    Endpoint to get number of chunks for a given party.
    """
    from app.src.milvus.milvus_interface import MilvusInterface

    interface = MilvusInterface()
    num_chunks = await interface.get_number_of_chunks_by_party(collection_name=collection_name, party=party)
    logger.info(f"[GET_CHUNKS] Collection: {collection_name}, Party: {party}, Num Chunks: {num_chunks}")

    return JSONResponse(content={"status": "GET_CHUNKS has started",})