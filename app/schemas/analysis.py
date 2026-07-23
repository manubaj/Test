"""Analysis, contact, technology, lead score, and report schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import (
    AnalysisStatus,
    ContactRole,
    ReportPriority,
    TechnologyCategory,
)
from app.schemas.common import ORMModel


class AnalysisCreate(BaseModel):
    company_id: UUID
    run_async: bool = Field(
        default=False,
        description="If true, enqueue a background job instead of running inline.",
    )


class AnalysisRead(ORMModel):
    id: UUID
    company_id: UUID
    status: AnalysisStatus
    website_intelligence: Optional[Any] = None
    erp_opportunity: Optional[Any] = None
    hiring_analysis: Optional[Any] = None
    overall_confidence: Optional[Decimal] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ContactRead(ORMModel):
    id: UUID
    company_id: UUID
    analysis_id: Optional[UUID] = None
    full_name: str
    title: Optional[str] = None
    role_category: ContactRole
    email: Optional[str] = None
    profile_url: Optional[str] = None
    source: Optional[str] = None


class TechnologyRead(ORMModel):
    id: UUID
    company_id: UUID
    analysis_id: Optional[UUID] = None
    name: str
    category: TechnologyCategory
    confidence: Optional[Decimal] = None
    evidence: Optional[str] = None
    version_hint: Optional[str] = None


class LeadScoreRead(ORMModel):
    id: UUID
    company_id: UUID
    analysis_id: UUID
    score: Decimal
    explanation: str
    factors: Any
    model_version: Optional[str] = None


class ReportRead(ORMModel):
    id: UUID
    company_id: UUID
    analysis_id: UUID
    executive_summary: str
    business_opportunity: str
    why_prospect: str
    recommended_services: Any
    estimated_deal_size: Optional[Decimal] = None
    estimated_deal_size_label: Optional[str] = None
    priority: ReportPriority
    next_action: str


class CompanyIntelligenceBundle(BaseModel):
    """Aggregated dashboard payload for a single company."""

    company_id: UUID
    analysis: Optional[AnalysisRead] = None
    contacts: list[ContactRead] = Field(default_factory=list)
    technologies: list[TechnologyRead] = Field(default_factory=list)
    lead_score: Optional[LeadScoreRead] = None
    report: Optional[ReportRead] = None
    news: list[dict[str, Any]] = Field(default_factory=list)
    agents: dict[str, Any] = Field(
        default_factory=dict,
        description="Outputs from the six analysis agents",
    )
    agent_trace: list[dict[str, Any]] = Field(default_factory=list)
