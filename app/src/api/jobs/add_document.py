"""
add document API job
"""
import logging
import uuid

from app.src.api import job_store
from app.src.api.models import Document
from app.src.chunking.pdf_chunker import pdf_chunker
from app.src.milvus.milvus_interface import MilvusInterface
from pydantic import HttpUrl

logger = logging.getLogger(__name__)


async def add_document_job(job_id: uuid.UUID, payload: dict):
    job_store.set_pending(str(job_id))
    try:
        documents = [Document(**d) for d in payload["documents"]]
        for document in documents:
            chunks = await pdf_chunker(HttpUrl(document.url), document.name, document.party, document.year)
            logger.info(f"[ADD_DOCUMENT] Document {document.name} chunked into {len(chunks)} chunks.")
            interface = MilvusInterface()
            await interface.insert_chunks(collection_name=document.collection_name, chunks=chunks)
            logger.info(f"[ADD_DOCUMENT] Document {document.name} added to collection {document.collection_name}.")
        job_store.set_completed(str(job_id), {"message": f"{len(documents)} document(s) added successfully."})
        logger.info(f"[ADD_DOCUMENT] Job {job_id} completed.")
    except Exception as exc:
        logger.exception(f"[ADD_DOCUMENT_FAILED] Job {job_id}: {exc}")
        job_store.set_failed(str(job_id), str(exc))
