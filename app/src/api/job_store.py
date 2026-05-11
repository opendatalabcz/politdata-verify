"""
Simple in-memory job result store for background tasks.
"""
from typing import Any, Dict

_store: Dict[str, dict] = {}


def set_pending(job_id: str) -> None:
    """mark job as pending (called immediately after enqueue)."""
    _store[str(job_id)] = {"status": "PENDING"}


def set_completed(job_id: str, result: Any) -> None:
    """store job result and mark as completed."""
    _store[str(job_id)] = {"status": "COMPLETED", "result": result}


def set_failed(job_id: str, error: str) -> None:
    """store error message and mark job as failed."""
    _store[str(job_id)] = {"status": "FAILED", "error": error}


def get_job(job_id: str) -> dict | None:
    """return job entry or None if the id is unknown."""
    return _store.get(str(job_id))
