"""Discovery orchestration — create runs immediately, execute agents in background."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.discovery import ERPDiscoveryTool
from app.agents.erp_catalog import all_offerings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.database.session import get_session_factory
from app.models.discovery import DiscoveryLead, DiscoveryRun
from app.models.enums import AnalysisStatus
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class DiscoveryRunRepository(BaseRepository[DiscoveryRun]):
    model = DiscoveryRun


class DiscoveryLeadRepository(BaseRepository[DiscoveryLead]):
    model = DiscoveryLead

    async def for_run(self, run_id: UUID) -> list[DiscoveryLead]:
        result = await self.session.execute(
            select(DiscoveryLead)
            .where(DiscoveryLead.run_id == run_id)
            .order_by(DiscoveryLead.lead_score.desc())
        )
        return list(result.scalars().all())


async def execute_discovery_run(run_id: UUID) -> None:
    """
    Execute the six discovery agents for an existing run.

    Uses a fresh DB session — safe for FastAPI BackgroundTasks.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        runs = DiscoveryRunRepository(session)
        leads_repo = DiscoveryLeadRepository(session)
        run = await runs.get(run_id)
        if not run:
            logger.error("Discovery run %s not found for execution", run_id)
            return

        run.status = AnalysisStatus.RUNNING
        run.summary = {
            "phase": "searching",
            "message": "Searching LinkedIn-indexed jobs and the public web…",
        }
        await session.commit()

        try:
            tool = ERPDiscoveryTool(target_lead_count=run.target_lead_count)
            result = await tool.run()

            for item in result.get("leads") or []:
                await leads_repo.add(
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
                "phase": "completed",
                "message": f"Found {run.leads_found} leads",
                "agent_trace": result.get("agent_trace"),
                "agents": result.get("agents"),
                "tool_version": result.get("tool_version"),
            }
            run.status = AnalysisStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            await session.commit()
            logger.info("Discovery run %s completed leads=%s", run_id, run.leads_found)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Discovery run %s failed", run_id)
            await session.rollback()
            # Re-load run after rollback
            run = await runs.get(run_id)
            if run:
                run.status = AnalysisStatus.FAILED
                run.error_message = str(exc)
                run.summary = {"phase": "failed", "message": str(exc)}
                run.completed_at = datetime.now(timezone.utc)
                await session.commit()


class DiscoveryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.runs = DiscoveryRunRepository(session)
        self.leads = DiscoveryLeadRepository(session)

    async def create_run(
        self,
        *,
        created_by: Optional[UUID] = None,
        target_lead_count: int = 100,
    ) -> DiscoveryRun:
        """Persist a RUNNING row immediately (HTTP returns before agents finish)."""
        run = DiscoveryRun(
            status=AnalysisStatus.RUNNING,
            target_lead_count=target_lead_count,
            offerings_searched=all_offerings(),
            created_by=created_by,
            started_at=datetime.now(timezone.utc),
            summary={
                "phase": "queued",
                "message": "Discovery queued — agents starting in background…",
            },
        )
        await self.runs.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_run(self, run_id: UUID) -> DiscoveryRun:
        run = await self.runs.get(run_id)
        if not run:
            raise NotFoundError("Discovery run not found")
        return run

    async def list_runs(self, *, limit: int = 20) -> list[DiscoveryRun]:
        result = await self.session.execute(
            select(DiscoveryRun).order_by(DiscoveryRun.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def leads_for_run(self, run_id: UUID) -> list[DiscoveryLead]:
        await self.get_run(run_id)
        return await self.leads.for_run(run_id)
