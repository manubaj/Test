"""
Security helpers: password hashing, JWT creation/validation, API key hashing.

Uses the ``bcrypt`` library directly (avoids known passlib/bcrypt version
compatibility issues that can break login after Docker rebuilds).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    # bcrypt has a 72-byte input limit; truncate defensively for safety
    raw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time password verification."""
    try:
        raw = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(raw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key with SHA-256.

    API keys are high-entropy secrets; SHA-256 is sufficient and fast for
    lookup comparisons. The plaintext key is shown once at creation time.
    """
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    """Generate a URL-safe random API key."""
    return secrets.token_urlsafe(32)


def create_access_token(
    subject: str | UUID,
    *,
    role: str,
    expires_minutes: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT; raise UnauthorizedError on failure."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
    if payload.get("type") != "access" or not payload.get("sub"):
        raise UnauthorizedError("Invalid token payload")
    return payload
