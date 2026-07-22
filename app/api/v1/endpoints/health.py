"""Health and readiness probes."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession
from app.core.config import get_settings
from app.repositories import UserRepository

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict:
    """Liveness probe (does not require DB)."""
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "llm_provider": settings.llm_provider,
    }


@router.get("/ready")
async def ready(db: DbSession) -> dict:
    """Readiness probe — DB reachable and admin user present."""
    settings = get_settings()
    await db.execute(text("SELECT 1"))
    admin = await UserRepository(db).get_by_email(
        settings.bootstrap_admin_email.lower()
    )
    return {
        "status": "ready" if admin else "degraded",
        "database": "ok",
        "admin_seeded": bool(admin and admin.is_active),
        "admin_email": settings.bootstrap_admin_email,
    }
