"""
Discovery ORM models — runs that find ~100 ERP demand leads globally.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AnalysisStatus, JobStatus


class DiscoveryRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One discovery execution targeting hardcoded ERP offerings."""

    __tablename__ = "discovery_runs"

    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(
            AnalysisStatus,
            name="discovery_run_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=AnalysisStatus.PENDING,
        server_default=AnalysisStatus.PENDING.value,
        index=True,
    )
    target_lead_count: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    leads_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    offerings_searched: Mapped[Any] = mapped_column(JSONB, nullable=False, default=list)
    query_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    leads: Mapped[list["DiscoveryLead"]] = relationship(
        "DiscoveryLead",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DiscoveryLead(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A prospect company discovered as needing an ERP offering."""

    __tablename__ = "discovery_leads"

    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("discovery_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    matched_offerings: Mapped[Any] = mapped_column(JSONB, nullable=False, default=list)
    demand_signals: Mapped[Any] = mapped_column(JSONB, nullable=False, default=list)
    source_urls: Mapped[Any] = mapped_column(JSONB, nullable=False, default=list)
    lead_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    score_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision_makers: Mapped[Any] = mapped_column(JSONB, nullable=False, default=list)
    company_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)

    run: Mapped["DiscoveryRun"] = relationship("DiscoveryRun", back_populates="leads")
