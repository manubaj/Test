"""
Report model — executive sales intelligence report (Agent 7).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReportPriority

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.company import Company


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Generated opportunity report for sales teams.

    Fields map directly to Agent 7 responsibilities:
    executive summary, business opportunity, why-prospect,
    recommended services, estimated deal size, priority, next action.
    """

    __tablename__ = "reports"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Company this report describes.",
    )
    analysis_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Source analysis for this report.",
    )
    executive_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Short executive summary for sales leadership.",
    )
    business_opportunity: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Described ERP/service opportunity.",
    )
    why_prospect: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Why this company is a qualified prospect.",
    )
    recommended_services: Mapped[Any] = mapped_column(
        JSONB,
        nullable=False,
        doc="List of recommended services (IFS upgrade, SAP support, etc.).",
    )
    estimated_deal_size: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        doc="Rough deal size estimate in USD.",
    )
    estimated_deal_size_label: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Optional band label (e.g. 50k-150k) when exact size unknown.",
    )
    priority: Mapped[ReportPriority] = mapped_column(
        Enum(
            ReportPriority,
            name="report_priority",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=ReportPriority.MEDIUM,
        server_default=ReportPriority.MEDIUM.value,
        index=True,
        doc="Sales priority ranking.",
    )
    next_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Recommended immediate next sales action.",
    )
    full_content: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Optional extended report body / sections.",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="reports",
        lazy="selectin",
    )
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="reports",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Report id={self.id} company_id={self.company_id} priority={self.priority}>"
