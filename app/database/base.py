"""
SQLAlchemy declarative base and shared column mixins.

Module 2 provides only the persistence foundation required by ORM models.
Engine/session wiring lands in later modules (Configuration / FastAPI setup).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp for default factories."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """
    Declarative base for all ORM models.

    Using a single metadata registry keeps Alembic autogenerate consistent
    once migrations are introduced.
    """

    # Allow subclasses to define typed annotations freely.
    type_annotation_map: dict[Any, Any] = {}


class TimestampMixin:
    """Created/updated audit columns shared by most tables."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=utc_now,
        doc="Row creation timestamp (UTC).",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=utc_now,
        onupdate=utc_now,
        doc="Row last-update timestamp (UTC).",
    )


class UUIDPrimaryKeyMixin:
    """
    UUID primary key mixin.

    UUIDs avoid sequential ID leakage across multi-tenant deployments and
    simplify client-side ID generation for async job pipelines.
    """

    id: Mapped[Any] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Primary key (UUID v4).",
    )
