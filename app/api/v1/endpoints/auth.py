"""Authentication endpoints: login, register, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession, enforce_rate_limit, require_roles
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    """Exchange email/password for a JWT access token."""
    users = UserRepository(db)
    user = await users.get_by_email(payload.email.lower())
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("User account is disabled")
    token = create_access_token(user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        username=user.username,
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_rate_limit)],
)
async def register(
    payload: UserCreate,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> User:
    """Admin-only user registration."""
    users = UserRepository(db)
    if await users.get_by_email(payload.email.lower()):
        raise ConflictError("Email already registered")
    if await users.get_by_username(payload.username):
        raise ConflictError("Username already taken")
    user = User(
        email=payload.email.lower(),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    return await users.add(user)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> User:
    """Return the authenticated user profile."""
    return user


@router.post("/api-key", response_model=MessageResponse)
async def rotate_api_key(user: CurrentUser, db: DbSession) -> MessageResponse:
    """Generate a new API key for the current user (returned once)."""
    raw = generate_api_key()
    user.api_key_hash = hash_api_key(raw)
    await db.flush()
    return MessageResponse(message=f"API key created (store securely): {raw}")
