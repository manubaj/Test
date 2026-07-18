"""
Analysis model — one intelligence run against a company.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AnalysisStatus

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.lead_score import LeadScore
    from app.models.report import Report
    from app.models.technology import Technology
    from app.models.user import User


class Analysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Persisted output of the multi-agent analysis pipeline.

    Agent-specific payloads are stored as JSONB so schema evolution does not
    require a migration for every prompt/output tweak.
    """

    __tablename__ = "analysis"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Company being analyzed.",
    )
    created_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="User who triggered the analysis (if authenticated).",
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(
            AnalysisStatus,
            name="analysis_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=AnalysisStatus.PENDING,
        server_default=AnalysisStatus.PENDING.value,
        index=True,
        doc="Current analysis lifecycle state.",
    )
    website_intelligence: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Agent 1 JSON output (products, ERP, cloud, industry, etc.).",
    )
    erp_opportunity: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Agent 2 JSON output (opportunity type + confidence).",
    )
    hiring_analysis: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Agent 4 JSON output (hiring signals + hiring score).",
    )
    raw_agent_outputs: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Optional full agent dump for debugging / replay.",
    )
    overall_confidence: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Pipeline-level confidence score (0–100).",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Failure details when status=failed.",
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When agent execution began.",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When agent execution finished.",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="analyses",
        lazy="selectin",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="analyses",
        lazy="selectin",
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="analysis",
        lazy="selectin",
    )
    technologies: Mapped[list["Technology"]] = relationship(
        "Technology",
        back_populates="analysis",
        lazy="selectin",
    )
    lead_scores: Mapped[list["LeadScore"]] = relationship(
        "LeadScore",
        back_populates="analysis",
        lazy="selectin",
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="analysis",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Analysis id={self.id} company_id={self.company_id} status={self.status}>"
