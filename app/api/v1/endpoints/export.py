"""CSV / Excel export endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.api.deps import CurrentUser, DbSession, enforce_rate_limit
from app.services.export import ExportService

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/csv", dependencies=[Depends(enforce_rate_limit)])
async def export_csv(
    db: DbSession,
    user: CurrentUser,
    company_id: list[UUID] | None = Query(default=None),
) -> Response:
    data = await ExportService(db).export_csv(company_id)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.get("/excel", dependencies=[Depends(enforce_rate_limit)])
async def export_excel(
    db: DbSession,
    user: CurrentUser,
    company_id: list[UUID] | None = Query(default=None),
) -> Response:
    data = await ExportService(db).export_excel(company_id)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=leads.xlsx"},
    )
