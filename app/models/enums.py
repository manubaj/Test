"""
Shared enumerations for ORM models.

Keeping enums in one module avoids circular imports between model files
and gives Alembic a single place to discover PostgreSQL ENUM types later.
"""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    """Role-based access control roles."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class AnalysisStatus(str, enum.Enum):
    """Lifecycle status for a company analysis run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobStatus(str, enum.Enum):
    """Background job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Supported asynchronous job kinds."""

    WEBSITE_CRAWL = "website_crawl"
    FULL_ANALYSIS = "full_analysis"
    REPORT_GENERATION = "report_generation"
    EXPORT_CSV = "export_csv"
    EXPORT_EXCEL = "export_excel"


class TechnologyCategory(str, enum.Enum):
    """High-level technology classification."""

    ERP = "erp"
    CRM = "crm"
    CLOUD = "cloud"
    DATABASE = "database"
    LANGUAGE = "language"
    DEVOPS = "devops"
    OTHER = "other"


class ContactRole(str, enum.Enum):
    """Decision-maker role categories extracted by Agent 5."""

    CEO = "ceo"
    CIO = "cio"
    CTO = "cto"
    VP_IT = "vp_it"
    IT_DIRECTOR = "it_director"
    ERP_MANAGER = "erp_manager"
    APPLICATION_MANAGER = "application_manager"
    DIGITAL_TRANSFORMATION_LEAD = "digital_transformation_lead"
    OTHER = "other"


class ReportPriority(str, enum.Enum):
    """Sales priority assigned by the Report Generator agent."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmployeeSizeBand(str, enum.Enum):
    """Coarse employee-count bands used for search filters."""

    MICRO = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1001-5000"
    GLOBAL = "5000+"
