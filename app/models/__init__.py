"""
SQLAlchemy ORM models for the AI Sales Intelligence Platform.

Importing this package registers every mapped class on ``Base.metadata``,
which Alembic and schema verification scripts rely on.
"""

from app.models.analysis import Analysis
from app.models.company import Company
from app.models.contact import Contact
from app.models.crawl_log import CrawlLog
from app.models.discovery import DiscoveryLead, DiscoveryRun
from app.models.enums import (
    AnalysisStatus,
    ContactRole,
    EmployeeSizeBand,
    JobStatus,
    JobType,
    ReportPriority,
    TechnologyCategory,
    UserRole,
)
from app.models.job import Job
from app.models.lead_score import LeadScore
from app.models.report import Report
from app.models.setting import Setting
from app.models.technology import Technology
from app.models.user import User

EXPECTED_TABLES: tuple[str, ...] = (
    "users",
    "settings",
    "companies",
    "analysis",
    "contacts",
    "technologies",
    "lead_scores",
    "crawl_logs",
    "jobs",
    "reports",
    "discovery_runs",
    "discovery_leads",
)

__all__ = [
    "Analysis",
    "AnalysisStatus",
    "Company",
    "Contact",
    "ContactRole",
    "CrawlLog",
    "DiscoveryLead",
    "DiscoveryRun",
    "EmployeeSizeBand",
    "EXPECTED_TABLES",
    "Job",
    "JobStatus",
    "JobType",
    "LeadScore",
    "Report",
    "ReportPriority",
    "Setting",
    "Technology",
    "TechnologyCategory",
    "User",
    "UserRole",
]
