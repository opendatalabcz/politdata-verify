"""
Simple in-memory job result store for background tasks.
"""
from typing import Any, Dict

_store: Dict[str, dict] = {}


def set_pending(job_id: str) -> None:
    _store[str(job_id)] = {"status": "PENDING"}


def set_completed(job_id: str, result: Any) -> None:
    _store[str(job_id)] = {"status": "COMPLETED", "result": result}


def set_failed(job_id: str, error: str) -> None:
    _store[str(job_id)] = {"status": "FAILED", "error": error}


def get_job(job_id: str) -> dict | None:
    return _store.get(str(job_id))
