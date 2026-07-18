"""
Company model — core prospect entity searchable by name, site, industry, etc.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EmployeeSizeBand

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.contact import Contact
    from app.models.crawl_log import CrawlLog
    from app.models.job import Job
    from app.models.lead_score import LeadScore
    from app.models.report import Report
    from app.models.technology import Technology


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Target company for ERP sales intelligence.

    Search APIs filter on name, website, country, industry, revenue,
    employee size, and related technology / ERP detections.
    """

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Legal or trading company name.",
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        unique=True,
        index=True,
        doc="Primary company website URL (normalized).",
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Headquarters or primary operating country.",
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
        doc="Industry vertical (manufacturing, logistics, etc.).",
    )
    revenue: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        doc="Approximate annual revenue in USD (if known).",
    )
    employee_size: Mapped[Optional[EmployeeSizeBand]] = mapped_column(
        Enum(
            EmployeeSizeBand,
            name="employee_size_band",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=True,
        index=True,
        doc="Employee headcount band for firmographic filtering.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Short company description from crawl or manual entry.",
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Public LinkedIn company page if available.",
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        doc="Primary city for geographic context.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
        doc="Soft-delete / archive flag.",
    )

    # Relationships — cascade deletes keep dependent intelligence consistent
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    technologies: Mapped[list["Technology"]] = relationship(
        "Technology",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    lead_scores: Mapped[list["LeadScore"]] = relationship(
        "LeadScore",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crawl_logs: Mapped[list["CrawlLog"]] = relationship(
        "CrawlLog",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="company",
        lazy="selectin",
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"
