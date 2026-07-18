"""
Lead score model — 0–100 prospect score with factor explanations.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.company import Company


class LeadScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Agent 6 lead score result.

    Example factor weights (configurable later):
    ERP Detected=30, Manufacturing=10, Hiring ERP=20,
    Cloud Migration=20, Expansion=20.
    """

    __tablename__ = "lead_scores"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Scored company.",
    )
    analysis_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Analysis that produced this score.",
    )
    score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        doc="Lead score from 0 to 100.",
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Human-readable scoring rationale.",
    )
    factors: Mapped[Any] = mapped_column(
        JSONB,
        nullable=False,
        doc="Structured factor breakdown, e.g. [{name, points, reason}].",
    )
    model_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Scoring rule / model version for reproducibility.",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="lead_scores",
        lazy="selectin",
    )
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="lead_scores",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<LeadScore id={self.id} score={self.score} company_id={self.company_id}>"
