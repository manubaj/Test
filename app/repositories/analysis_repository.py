"""Repositories for analysis outputs and related intelligence rows."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.contact import Contact
from app.models.crawl_log import CrawlLog
from app.models.job import Job
from app.models.lead_score import LeadScore
from app.models.report import Report
from app.models.technology import Technology
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    model = Analysis

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def latest_for_company(self, company_id: UUID) -> Optional[Analysis]:
        result = await self.session.execute(
            select(Analysis)
            .where(Analysis.company_id == company_id)
            .order_by(Analysis.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ContactRepository(BaseRepository[Contact]):
    model = Contact

    async def for_company(self, company_id: UUID) -> list[Contact]:
        result = await self.session.execute(
            select(Contact).where(Contact.company_id == company_id)
        )
        return list(result.scalars().all())


class TechnologyRepository(BaseRepository[Technology]):
    model = Technology

    async def for_company(self, company_id: UUID) -> list[Technology]:
        result = await self.session.execute(
            select(Technology).where(Technology.company_id == company_id)
        )
        return list(result.scalars().all())


class LeadScoreRepository(BaseRepository[LeadScore]):
    model = LeadScore

    async def latest_for_company(self, company_id: UUID) -> Optional[LeadScore]:
        result = await self.session.execute(
            select(LeadScore)
            .where(LeadScore.company_id == company_id)
            .order_by(LeadScore.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ReportRepository(BaseRepository[Report]):
    model = Report

    async def latest_for_company(self, company_id: UUID) -> Optional[Report]:
        result = await self.session.execute(
            select(Report)
            .where(Report.company_id == company_id)
            .order_by(Report.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class CrawlLogRepository(BaseRepository[CrawlLog]):
    model = CrawlLog


class JobRepository(BaseRepository[Job]):
    model = Job
