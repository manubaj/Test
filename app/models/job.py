"""
Job model — asynchronous work items (crawl, analysis, export).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import JobStatus, JobType

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Background job record for long-running agent or export work.

    The API can enqueue a job and poll status without blocking HTTP workers.
    """

    __tablename__ = "jobs"

    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="job_type", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        index=True,
        doc="Kind of work this job performs.",
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=JobStatus.PENDING,
        server_default=JobStatus.PENDING.value,
        index=True,
        doc="Current job lifecycle status.",
    )
    company_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Related company when applicable.",
    )
    created_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="User who enqueued the job.",
    )
    payload: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Input parameters for the job worker.",
    )
    result: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Structured result payload on completion.",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Failure details when status=failed.",
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Worker start timestamp.",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Worker completion timestamp.",
    )

    company: Mapped[Optional["Company"]] = relationship(
        "Company",
        back_populates="jobs",
        lazy="selectin",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="jobs",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} type={self.job_type} status={self.status}>"
