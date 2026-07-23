"""Analysis, intelligence bundle, and website analysis endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession, enforce_rate_limit, require_roles
from app.core.exceptions import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import (
    AnalysisRepository,
    CompanyRepository,
    ContactRepository,
    LeadScoreRepository,
    ReportRepository,
    TechnologyRepository,
)
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisRead,
    CompanyIntelligenceBundle,
    ContactRead,
    LeadScoreRead,
    ReportRead,
    TechnologyRead,
)
from app.services.analysis import AnalysisService
from app.services.crawler import WebsiteCrawler

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analysis",
    response_model=AnalysisRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_rate_limit)],
)
async def run_analysis(
    payload: AnalysisCreate,
    db: DbSession,
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> AnalysisRead:
    """Run the full multi-agent intelligence pipeline for a company."""
    service = AnalysisService(db)
    analysis = await service.run_for_company(payload.company_id, created_by=user.id)
    return analysis


@router.get("/analysis/{analysis_id}", response_model=AnalysisRead)
async def get_analysis(
    analysis_id: UUID, db: DbSession, user: CurrentUser
) -> AnalysisRead:
    analysis = await AnalysisRepository(db).get(analysis_id)
    if not analysis:
        raise NotFoundError("Analysis not found")
    return analysis


@router.get(
    "/companies/{company_id}/intelligence",
    response_model=CompanyIntelligenceBundle,
)
async def company_intelligence(
    company_id: UUID, db: DbSession, user: CurrentUser
) -> CompanyIntelligenceBundle:
    """Dashboard aggregate: analysis, contacts, tech, score, report, news."""
    company = await CompanyRepository(db).get(company_id)
    if not company:
        raise NotFoundError("Company not found")

    analysis = await AnalysisRepository(db).latest_for_company(company_id)
    contacts = await ContactRepository(db).for_company(company_id)
    technologies = await TechnologyRepository(db).for_company(company_id)
    score = await LeadScoreRepository(db).latest_for_company(company_id)
    report = await ReportRepository(db).latest_for_company(company_id)

    news = []
    agents: dict = {}
    agent_trace: list = []
    if analysis and isinstance(analysis.raw_agent_outputs, dict):
        news = analysis.raw_agent_outputs.get("news") or []
        agents = analysis.raw_agent_outputs.get("agents") or {}
        agent_trace = analysis.raw_agent_outputs.get("agent_trace") or []

    return CompanyIntelligenceBundle(
        company_id=company_id,
        analysis=analysis,
        contacts=contacts,
        technologies=technologies,
        lead_score=score,
        report=report,
        news=news,
        agents=agents,
        agent_trace=agent_trace,
    )


@router.get("/companies/{company_id}/contacts", response_model=list[ContactRead])
async def list_contacts(company_id: UUID, db: DbSession, user: CurrentUser):
    return await ContactRepository(db).for_company(company_id)


@router.get("/companies/{company_id}/technologies", response_model=list[TechnologyRead])
async def list_technologies(company_id: UUID, db: DbSession, user: CurrentUser):
    return await TechnologyRepository(db).for_company(company_id)


@router.get("/companies/{company_id}/lead-score", response_model=LeadScoreRead | None)
async def get_lead_score(company_id: UUID, db: DbSession, user: CurrentUser):
    return await LeadScoreRepository(db).latest_for_company(company_id)


@router.get("/companies/{company_id}/report", response_model=ReportRead | None)
async def get_report(company_id: UUID, db: DbSession, user: CurrentUser):
    return await ReportRepository(db).latest_for_company(company_id)


@router.post(
    "/website/analyze",
    dependencies=[Depends(enforce_rate_limit)],
)
async def analyze_website_preview(
    url: str,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> dict:
    """Quick website crawl preview without persisting an analysis."""
    result = await WebsiteCrawler().crawl(url, max_pages=3)
    return result.to_dict()
