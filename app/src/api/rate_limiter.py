import time
from collections import defaultdict
from fastapi import HTTPException, Request

MAX_CALLS_PER_HOUR = 5
MAX_CHARS_PER_DAY = 5000
MAX_INPUT_CHARS = 5000
MAX_QUERY_CHARS = 500

_calls: dict[str, list[float]] = defaultdict(list)
_chars: dict[str, tuple[float, int]] = {}


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def check_rate_limit(request: Request, text: str) -> None:
    ip = _get_ip(request)
    now = time.time()

    if len(text) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"Vstupní text je příliš dlouhý. Maximum je {MAX_INPUT_CHARS} znaků."
        )

    # calls per hour
    _calls[ip] = [t for t in _calls[ip] if now - t < 3600]
    if len(_calls[ip]) >= MAX_CALLS_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail=f"Překročil jsi limit {MAX_CALLS_PER_HOUR} ověření za hodinu. Zkus to znovu za chvíli nebo nás kontaktuj pro rozšíření přístupu."
        )

    # chars per day
    window_start, used = _chars.get(ip, (now, 0))
    if now - window_start > 86400:
        window_start, used = now, 0
    if used + len(text) > MAX_CHARS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail=f"Překročil jsi denní limit {MAX_CHARS_PER_DAY} znaků. Limit se obnoví za 24 hodin nebo nás kontaktuj pro rozšíření přístupu."
        )

    _calls[ip].append(now)
    _chars[ip] = (window_start, used + len(text))
