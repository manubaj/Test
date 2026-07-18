"""
Technology model — detected ERP / cloud / database / platform signals.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import TechnologyCategory

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.company import Company


class Technology(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Normalized technology detection row produced by Agent 3.

    Examples: IFS Cloud, SAP S/4HANA, Azure, PostgreSQL, Kubernetes.
    """

    __tablename__ = "technologies"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "name",
            "analysis_id",
            name="uq_technologies_company_name_analysis",
        ),
    )

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Company where the technology was detected.",
    )
    analysis_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("analysis.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Analysis run that produced this detection.",
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        doc="Canonical technology name (e.g. IFS Cloud, SAP ECC).",
    )
    category: Mapped[TechnologyCategory] = mapped_column(
        Enum(
            TechnologyCategory,
            name="technology_category",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=TechnologyCategory.OTHER,
        server_default=TechnologyCategory.OTHER.value,
        index=True,
        doc="Technology category for filtering and scoring.",
    )
    confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Detection confidence (0–100).",
    )
    evidence: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Snippet or URL supporting the detection.",
    )
    version_hint: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Optional version string if mentioned on-site.",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="technologies",
        lazy="selectin",
    )
    analysis: Mapped[Optional["Analysis"]] = relationship(
        "Analysis",
        back_populates="technologies",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Technology id={self.id} name={self.name!r} category={self.category}>"
