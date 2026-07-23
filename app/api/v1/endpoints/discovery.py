"""ERP demand discovery REST endpoints."""

from __future__ import annotations

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.agents.discovery import ERPDiscoveryTool
from app.agents.erp_catalog import all_offerings
from app.api.deps import CurrentUser, DbSession, enforce_rate_limit, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import ORMModel
from app.services.discovery import DiscoveryService

router = APIRouter(prefix="/discovery", tags=["ERP Demand Discovery"])


class DiscoveryRunCreate(BaseModel):
    target_lead_count: int = Field(default=100, ge=10, le=100)


class DiscoveryRunRead(ORMModel):
    id: UUID
    status: str
    target_lead_count: int
    leads_found: int
    query_count: int
    error_message: str | None = None
    summary: dict | list | None = None


class DiscoveryLeadRead(ORMModel):
    id: UUID
    run_id: UUID
    company_name: str
    website: str | None = None
    linkedin_url: str | None = None
    country: str | None = None
    location: str | None = None
    industry: str | None = None
    matched_offerings: list | dict | None = None
    demand_signals: list | dict | None = None
    source_urls: list | dict | None = None
    lead_score: float | int | None = None
    score_explanation: str | None = None
    decision_makers: list | dict | None = None
    company_summary: str | None = None


@router.get("/offerings")
async def list_offerings(user: CurrentUser) -> dict:
    """Hardcoded ERP offerings used as discovery input (no manual entry)."""
    return {"count": len(all_offerings()), "offerings": all_offerings()}


@router.get("/agents")
async def list_discovery_agents(user: CurrentUser) -> dict:
    tool = ERPDiscoveryTool()
    return {"tool": tool.name, "version": tool.version, "agents": tool.list_agents()}


@router.post(
    "/runs",
    response_model=DiscoveryRunRead,
    dependencies=[Depends(enforce_rate_limit)],
)
async def start_discovery_run(
    payload: DiscoveryRunCreate,
    db: DbSession,
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> DiscoveryRunRead:
    """
    Start a global discovery run.

    Searches LinkedIn-indexed + web signals for companies needing hardcoded
    ERP offerings and returns up to ``target_lead_count`` leads (default 100).
    """
    service = DiscoveryService(db)
    run = await service.start_run(
        created_by=user.id,
        target_lead_count=payload.target_lead_count,
    )
    return run


@router.get("/runs", response_model=list[DiscoveryRunRead])
async def list_runs(db: DbSession, user: CurrentUser) -> list[DiscoveryRunRead]:
    return await DiscoveryService(db).list_runs()


@router.get("/runs/{run_id}", response_model=DiscoveryRunRead)
async def get_run(run_id: UUID, db: DbSession, user: CurrentUser) -> DiscoveryRunRead:
    return await DiscoveryService(db).get_run(run_id)


@router.get("/runs/{run_id}/leads", response_model=list[DiscoveryLeadRead])
async def get_leads(
    run_id: UUID,
    db: DbSession,
    user: CurrentUser,
    limit: int = Query(default=100, ge=1, le=100),
) -> list[DiscoveryLeadRead]:
    leads = await DiscoveryService(db).leads_for_run(run_id)
    return leads[:limit]


@router.get("/runs/{run_id}/export/csv")
async def export_leads_csv(run_id: UUID, db: DbSession, user: CurrentUser) -> Response:
    leads = await DiscoveryService(db).leads_for_run(run_id)
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "company_name",
            "website",
            "linkedin_url",
            "location",
            "industry",
            "matched_offerings",
            "lead_score",
            "contact_name",
            "designation",
            "email",
            "phone",
            "contact_location",
        ],
    )
    writer.writeheader()
    for lead in leads:
        contacts = lead.decision_makers or [{}]
        if not isinstance(contacts, list) or not contacts:
            contacts = [{}]
        for person in contacts:
            if not isinstance(person, dict):
                person = {}
            writer.writerow(
                {
                    "company_name": lead.company_name,
                    "website": lead.website or "",
                    "linkedin_url": lead.linkedin_url or "",
                    "location": lead.location or "",
                    "industry": lead.industry or "",
                    "matched_offerings": "; ".join(lead.matched_offerings or []),
                    "lead_score": str(lead.lead_score),
                    "contact_name": person.get("name") or "",
                    "designation": person.get("designation") or "",
                    "email": person.get("email") or "",
                    "phone": person.get("phone") or "",
                    "contact_location": person.get("location") or lead.location or "",
                }
            )
    return Response(
        content=buffer.getvalue().encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=discovery_{run_id}.csv"},
    )


@router.get("/runs/{run_id}/export/excel")
async def export_leads_excel(run_id: UUID, db: DbSession, user: CurrentUser) -> Response:
    from openpyxl import Workbook

    leads = await DiscoveryService(db).leads_for_run(run_id)
    wb = Workbook()
    ws = wb.active
    ws.title = "Discovery Leads"
    ws.append(
        [
            "Company",
            "Website",
            "LinkedIn",
            "Location",
            "Industry",
            "ERP Offerings",
            "Score",
            "Contact Name",
            "Designation",
            "Email",
            "Phone",
        ]
    )
    for lead in leads:
        contacts = lead.decision_makers if isinstance(lead.decision_makers, list) else []
        if not contacts:
            contacts = [{}]
        for person in contacts:
            if not isinstance(person, dict):
                person = {}
            ws.append(
                [
                    lead.company_name,
                    lead.website or "",
                    lead.linkedin_url or "",
                    lead.location or "",
                    lead.industry or "",
                    "; ".join(lead.matched_offerings or []),
                    float(lead.lead_score),
                    person.get("name") or "",
                    person.get("designation") or "",
                    person.get("email") or "",
                    person.get("phone") or "",
                ]
            )
    stream = io.BytesIO()
    wb.save(stream)
    return Response(
        content=stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=discovery_{run_id}.xlsx"},
    )
