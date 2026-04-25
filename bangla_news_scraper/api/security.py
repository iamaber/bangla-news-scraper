import secrets
import threading
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

from bangla_news_scraper.config import settings

_rate_lock = threading.Lock()
_rate_window_seconds = 60.0
_request_log: dict[str, deque[float]] = defaultdict(deque)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")


def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    limit = settings.max_requests_per_minute_per_ip
    with _rate_lock:
        history = _request_log[client_ip]
        while history and now - history[0] > _rate_window_seconds:
            history.popleft()
        if len(history) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        history.append(now)
