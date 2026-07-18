"""
Settings model — system-wide and per-user configuration key/value pairs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Setting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Flexible configuration store.

    - ``user_id IS NULL`` → global / system setting
    - ``user_id`` set → user-scoped override
    Values are JSON so LLM provider switches (Ollama vs OpenAI) can be
    represented without schema changes.
    """

    __tablename__ = "settings"
    __table_args__ = (
        UniqueConstraint("key", "user_id", name="uq_settings_key_user"),
    )

    key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        doc="Setting key, e.g. llm.provider or crawler.max_pages.",
    )
    value: Mapped[Any] = mapped_column(
        JSONB,
        nullable=False,
        doc="JSON-encoded setting value.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Human-readable explanation of the setting.",
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="Owning user; NULL means system-wide setting.",
    )

    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="settings",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Setting key={self.key!r} user_id={self.user_id}>"
