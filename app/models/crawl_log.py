"""
Crawl log model — audit trail for website crawl attempts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company


class CrawlLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One crawl attempt against a company URL (or careers sub-page).

    Useful for debugging Playwright failures, robots restrictions,
    and measuring crawl cost/latency.
    """

    __tablename__ = "crawl_logs"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Company associated with this crawl.",
    )
    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        doc="URL that was requested.",
    )
    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Whether usable content was extracted.",
    )
    status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="HTTP status code if available.",
    )
    pages_crawled: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        doc="Number of pages successfully visited in this run.",
    )
    duration_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Wall-clock crawl duration in milliseconds.",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Error details when success=false.",
    )
    metadata_json: Mapped[Optional[Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        doc="Optional crawl metadata (user-agent, depth, content hashes).",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="crawl_logs",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CrawlLog id={self.id} url={self.url!r} success={self.success}>"
