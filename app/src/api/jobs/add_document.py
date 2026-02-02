"""
This module defines an API endpoint for adding a document to the system.
"""

import logging
import uuid
from fastapi.responses import JSONResponse

from app.src.api.models import DocumentPayload, Document
from app.src.chunking.pdf_chunker import pdf_chunker
from app.src.milvus.milvus_interface import MilvusInterface
from pydantic import HttpUrl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_document_job(job_id: uuid.UUID, payload: DocumentPayload):
    """
    Placeholder function for adding a document job.
    """
    documents = [Document(**d) for d in payload["documents"]]
    for document in documents:
        chunks = await pdf_chunker(HttpUrl(document.url), document.name, document.party, document.year)
        logger.info(f"[ADD_DOCUMENT] Document {document.name} chunked into {len(chunks)} chunks.")
        interface = MilvusInterface()
        await interface.insert_chunks(
            collection_name=document.collection_name,
            chunks=chunks
        )
        logger.info(f"[ADD_DOCUMENT] Document {document.name} added to collection {document.collection_name}.")

    logger.info(f"[ADD_DOCUMENT] Job {job_id} completed with {len(documents)} documents added.")
    return JSONResponse(content={"status": "ADD_DOCUMENT has started",})