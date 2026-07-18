"""
Simple in-memory sliding-window rate limiter.

Suitable for single-process / Docker Compose demos. Replace with Redis
for multi-replica production deployments.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque

from app.core.config import get_settings
from app.core.exceptions import RateLimitError


class RateLimiter:
    """Per-key request rate limiter."""

    def __init__(self) -> None:
        self._hits: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        """Raise RateLimitError when the key exceeds configured limits."""
        settings = get_settings()
        now = time.monotonic()
        window = float(settings.rate_limit_window_seconds)
        limit = settings.rate_limit_requests

        with self._lock:
            bucket = self._hits[key]
            # Drop timestamps outside the window
            while bucket and (now - bucket[0]) > window:
                bucket.popleft()
            if len(bucket) >= limit:
                raise RateLimitError(
                    f"Rate limit exceeded: {limit} requests per {int(window)}s"
                )
            bucket.append(now)


rate_limiter = RateLimiter()
