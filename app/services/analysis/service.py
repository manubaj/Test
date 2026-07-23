"""
Analysis orchestration service.

Runs the LangGraph workflow and persists agent outputs into ORM tables.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.workflow import run_analysis_workflow
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.analysis import Analysis
from app.models.contact import Contact
from app.models.crawl_log import CrawlLog
from app.models.enums import (
    AnalysisStatus,
    ContactRole,
    ReportPriority,
    TechnologyCategory,
)
from app.models.lead_score import LeadScore
from app.models.report import Report
from app.models.technology import Technology
from app.repositories import (
    AnalysisRepository,
    CompanyRepository,
    ContactRepository,
    CrawlLogRepository,
    LeadScoreRepository,
    ReportRepository,
    TechnologyRepository,
)

logger = get_logger(__name__)


class AnalysisService:
    """Coordinates crawl → agents → persistence for one company."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.companies = CompanyRepository(session)
        self.analyses = AnalysisRepository(session)
        self.contacts = ContactRepository(session)
        self.technologies = TechnologyRepository(session)
        self.scores = LeadScoreRepository(session)
        self.reports = ReportRepository(session)
        self.crawl_logs = CrawlLogRepository(session)

    async def run_for_company(
        self,
        company_id: UUID,
        *,
        created_by: Optional[UUID] = None,
    ) -> Analysis:
        company = await self.companies.get(company_id)
        if not company:
            raise NotFoundError("Company not found")
        if not company.website:
            raise NotFoundError("Company website is required for analysis")

        analysis = Analysis(
            company_id=company.id,
            created_by=created_by,
            status=AnalysisStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        await self.analyses.add(analysis)

        try:
            state = await run_analysis_workflow(
                company_name=company.name,
                website=company.website,
                country=company.country,
                industry=company.industry,
            )
            await self._persist_state(company.id, analysis, state)

            # Update firmographics when agents discover industry
            detected_industry = (state.get("website_intelligence") or {}).get("industry")
            if detected_industry and not company.industry:
                company.industry = detected_industry

            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.now(timezone.utc)
            analysis.overall_confidence = Decimal(
                str((state.get("erp_opportunity") or {}).get("confidence") or 0)
            )
            await self.session.flush()
            await self.session.refresh(analysis)
            return analysis
        except Exception as exc:  # noqa: BLE001
            # Persist FAILED status without re-raising so the request transaction
            # can commit the audit trail (caller inspects analysis.status).
            logger.exception("Analysis failed for company %s", company_id)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(exc)
            analysis.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(analysis)
            return analysis

    async def _persist_state(
        self, company_id: UUID, analysis: Analysis, state: dict
    ) -> None:
        analysis.website_intelligence = state.get("website_intelligence")
        analysis.erp_opportunity = state.get("erp_opportunity")
        analysis.hiring_analysis = state.get("hiring_analysis")
        analysis.raw_agent_outputs = {
            "technologies": state.get("technologies"),
            "decision_makers": state.get("decision_makers"),
            "lead_score": state.get("lead_score"),
            "report": state.get("report"),
            "news": state.get("news"),
            "agent_trace": state.get("agent_trace"),
            "technology_detection": state.get("technology_detection"),
            "decision_maker_finder": state.get("decision_maker_finder"),
            "agents": {
                "agent_1_website_intelligence": state.get("website_intelligence"),
                "agent_2_erp_opportunity": state.get("erp_opportunity"),
                "agent_3_technology_detection": state.get("technology_detection"),
                "agent_4_hiring_intelligence": state.get("hiring_analysis"),
                "agent_5_decision_maker_finder": state.get("decision_maker_finder"),
                "agent_6_lead_scoring": state.get("lead_score"),
            },
        }

        crawl = state.get("crawl") or {}
        await self.crawl_logs.add(
            CrawlLog(
                company_id=company_id,
                url=crawl.get("seed_url") or "",
                success=bool(crawl.get("success")),
                status_code=200 if crawl.get("success") else None,
                pages_crawled=int(crawl.get("pages_crawled") or 0),
                duration_ms=crawl.get("duration_ms"),
                error_message=crawl.get("error_message"),
                metadata_json=crawl.get("metadata"),
            )
        )

        for tech in state.get("technologies") or []:
            category = tech.get("category") or "other"
            try:
                cat_enum = TechnologyCategory(category)
            except ValueError:
                cat_enum = TechnologyCategory.OTHER
            await self.technologies.add(
                Technology(
                    company_id=company_id,
                    analysis_id=analysis.id,
                    name=tech["name"],
                    category=cat_enum,
                    confidence=Decimal(str(tech.get("confidence") or 0)),
                    evidence=tech.get("evidence"),
                    version_hint=tech.get("version_hint"),
                )
            )

        for person in state.get("decision_makers") or []:
            role = person.get("role_category") or "other"
            try:
                role_enum = ContactRole(role)
            except ValueError:
                role_enum = ContactRole.OTHER
            await self.contacts.add(
                Contact(
                    company_id=company_id,
                    analysis_id=analysis.id,
                    full_name=person.get("full_name") or "Unknown",
                    title=person.get("title"),
                    role_category=role_enum,
                    email=person.get("email"),
                    profile_url=person.get("profile_url"),
                    source=person.get("source"),
                )
            )

        lead = state.get("lead_score") or {}
        if lead:
            await self.scores.add(
                LeadScore(
                    company_id=company_id,
                    analysis_id=analysis.id,
                    score=Decimal(str(lead.get("score") or 0)),
                    explanation=lead.get("explanation") or "",
                    factors=lead.get("factors") or [],
                    model_version=lead.get("model_version"),
                )
            )

        report = state.get("report") or {}
        if report:
            priority_raw = report.get("priority") or "medium"
            try:
                priority = ReportPriority(priority_raw)
            except ValueError:
                priority = ReportPriority.MEDIUM
            await self.reports.add(
                Report(
                    company_id=company_id,
                    analysis_id=analysis.id,
                    executive_summary=report.get("executive_summary") or "",
                    business_opportunity=report.get("business_opportunity") or "",
                    why_prospect=report.get("why_prospect") or "",
                    recommended_services=report.get("recommended_services") or [],
                    estimated_deal_size=(
                        Decimal(str(report["estimated_deal_size"]))
                        if report.get("estimated_deal_size") is not None
                        else None
                    ),
                    estimated_deal_size_label=report.get("estimated_deal_size_label"),
                    priority=priority,
                    next_action=report.get("next_action") or "",
                    full_content=report.get("full_content"),
                )
            )
