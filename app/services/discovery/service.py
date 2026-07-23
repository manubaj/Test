"""Discovery orchestration — run agents and persist ~100 leads."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.discovery import ERPDiscoveryTool
from app.agents.erp_catalog import all_offerings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.discovery import DiscoveryLead, DiscoveryRun
from app.models.enums import AnalysisStatus
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class DiscoveryRunRepository(BaseRepository[DiscoveryRun]):
    model = DiscoveryRun


class DiscoveryLeadRepository(BaseRepository[DiscoveryLead]):
    model = DiscoveryLead

    async def for_run(self, run_id: UUID) -> list[DiscoveryLead]:
        from sqlalchemy import select

        result = await self.session.execute(
            select(DiscoveryLead)
            .where(DiscoveryLead.run_id == run_id)
            .order_by(DiscoveryLead.lead_score.desc())
        )
        return list(result.scalars().all())


class DiscoveryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.runs = DiscoveryRunRepository(session)
        self.leads = DiscoveryLeadRepository(session)

    async def start_run(
        self,
        *,
        created_by: Optional[UUID] = None,
        target_lead_count: int = 100,
    ) -> DiscoveryRun:
        run = DiscoveryRun(
            status=AnalysisStatus.RUNNING,
            target_lead_count=target_lead_count,
            offerings_searched=all_offerings(),
            created_by=created_by,
            started_at=datetime.now(timezone.utc),
        )
        await self.runs.add(run)

        try:
            tool = ERPDiscoveryTool(target_lead_count=target_lead_count)
            result = await tool.run()
            for item in result.get("leads") or []:
                await self.leads.add(
                    DiscoveryLead(
                        run_id=run.id,
                        company_name=item.get("company_name") or "Unknown",
                        website=item.get("website"),
                        linkedin_url=item.get("linkedin_url"),
                        country=item.get("country"),
                        location=item.get("location"),
                        industry=item.get("industry"),
                        matched_offerings=item.get("matched_offerings") or [],
                        demand_signals=item.get("demand_signals") or [],
                        source_urls=item.get("source_urls") or [],
                        lead_score=Decimal(str(item.get("lead_score") or 0)),
                        score_explanation=item.get("score_explanation"),
                        decision_makers=item.get("decision_makers") or [],
                        company_summary=item.get("company_summary"),
                        raw_payload=item,
                    )
                )
            run.leads_found = len(result.get("leads") or [])
            run.query_count = int(result.get("query_count") or 0)
            run.summary = {
                "agent_trace": result.get("agent_trace"),
                "agents": result.get("agents"),
                "tool_version": result.get("tool_version"),
            }
            run.status = AnalysisStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(run)
            return run
        except Exception as exc:  # noqa: BLE001
            logger.exception("Discovery run failed")
            run.status = AnalysisStatus.FAILED
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(run)
            return run

    async def get_run(self, run_id: UUID) -> DiscoveryRun:
        run = await self.runs.get(run_id)
        if not run:
            raise NotFoundError("Discovery run not found")
        return run

    async def list_runs(self, *, limit: int = 20) -> list[DiscoveryRun]:
        from sqlalchemy import select

        result = await self.session.execute(
            select(DiscoveryRun).order_by(DiscoveryRun.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def leads_for_run(self, run_id: UUID) -> list[DiscoveryLead]:
        await self.get_run(run_id)
        return await self.leads.for_run(run_id)
