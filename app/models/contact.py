"""
Contact model — decision makers linked to a company / analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ContactRole

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.company import Company


class Contact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Publicly discoverable decision maker (Agent 5 output).

    Profile links are stored when available from public pages only —
    no paid enrichment APIs are required.
    """

    __tablename__ = "contacts"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Company this contact belongs to.",
    )
    analysis_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("analysis.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Analysis run that discovered this contact.",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Contact full name.",
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Job title as published (e.g. Chief Information Officer).",
    )
    role_category: Mapped[ContactRole] = mapped_column(
        Enum(
            ContactRole,
            name="contact_role",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=ContactRole.OTHER,
        server_default=ContactRole.OTHER.value,
        index=True,
        doc="Normalized decision-maker role category.",
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True,
        doc="Public email if explicitly published.",
    )
    profile_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Public profile URL (LinkedIn/company leadership page).",
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Discovery source URL or method label.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional analyst notes.",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="contacts",
        lazy="selectin",
    )
    analysis: Mapped[Optional["Analysis"]] = relationship(
        "Analysis",
        back_populates="contacts",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Contact id={self.id} name={self.full_name!r} role={self.role_category}>"
