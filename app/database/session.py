"""
Async SQLAlchemy engine and session factory.

Engine is created lazily so Docker/env DATABASE_URL is always read at runtime
(not frozen at import time from a missing/wrong .env).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return (and cache) the async engine using current settings."""
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            future=True,
        )
        _session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


# Backwards-compatible aliases used by main.py / deps
def AsyncSessionLocal() -> AsyncSession:  # type: ignore[misc]
    """Create a new async session (call as context manager)."""
    return get_session_factory()()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a request-scoped async session.

    Commits only on success; rolls back when the endpoint raises.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()


async def init_db() -> None:
    """Create all tables (dev bootstrap). Prefer Alembic in production."""
    from app.database.base import Base
    import app.models  # noqa: F401 — register models

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
