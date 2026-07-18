"""Text normalization helpers used by crawler and agents."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse


_WS_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace and strip edges."""
    return _WS_RE.sub(" ", text or "").strip()


def normalize_url(url: str) -> str:
    """Ensure URL has a scheme and drop fragments."""
    value = (url or "").strip()
    if not value:
        return value
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    cleaned = parsed._replace(fragment="")
    return cleaned.geturl().rstrip("/")


def same_domain(base: str, candidate: str) -> bool:
    """Return True when candidate belongs to the same registrable host."""
    b = urlparse(base)
    c = urlparse(urljoin(base, candidate))
    return b.netloc.lower().replace("www.", "") == c.netloc.lower().replace("www.", "")


def extract_emails(text: str) -> list[str]:
    """Extract simple email addresses from free text."""
    return sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
