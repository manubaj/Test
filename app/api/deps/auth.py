"""FastAPI dependencies for JWT, API key, RBAC, and rate limiting."""

from __future__ import annotations

from typing import Annotated, Callable, Optional
from uuid import UUID

from fastapi import Depends, Header, Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.rate_limit import rate_limiter
from app.core.security import decode_access_token, hash_api_key
from app.database.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def enforce_rate_limit(request: Request) -> None:
    """Apply per-client rate limits using IP + optional API key."""
    client = request.client.host if request.client else "unknown"
    api_key = request.headers.get(get_settings().api_key_header, "")
    rate_limiter.check(f"{client}:{api_key[:8]}")


async def get_current_user(
    db: DbSession,
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Security(bearer_scheme)
    ] = None,
    api_key: Annotated[Optional[str], Security(api_key_scheme)] = None,
) -> User:
    """
    Resolve the current user from JWT Bearer token or X-API-Key header.
    """
    users = UserRepository(db)

    if credentials and credentials.scheme.lower() == "bearer":
        payload = decode_access_token(credentials.credentials)
        user = await users.get(UUID(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedError("User inactive or not found")
        return user

    if api_key:
        user = await users.get_by_api_key_hash(hash_api_key(api_key))
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid API key")
        return user

    raise UnauthorizedError("Authentication required (Bearer token or API key)")


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable:
    """Dependency factory enforcing RBAC roles."""

    async def _checker(user: CurrentUser) -> User:
        if user.role == UserRole.ADMIN:
            return user
        if user.role not in roles:
            raise ForbiddenError("Insufficient role permissions")
        return user

    return _checker
