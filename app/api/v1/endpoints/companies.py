"""Company CRUD and search endpoints."""

from __future__ import annotations

import math

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, enforce_rate_limit, require_roles
from app.core.exceptions import ConflictError, NotFoundError
from app.models.company import Company
from app.models.enums import EmployeeSizeBand, UserRole
from app.models.user import User
from app.repositories import CompanyRepository
from app.schemas.common import MessageResponse, Page
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.utils.text import normalize_url

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_rate_limit)],
)
async def create_company(
    payload: CompanyCreate,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> Company:
    repo = CompanyRepository(db)
    website = normalize_url(payload.website) if payload.website else None
    if website and await repo.get_by_website(website):
        raise ConflictError("Company with this website already exists")
    company = Company(
        name=payload.name,
        website=website,
        country=payload.country,
        industry=payload.industry,
        revenue=payload.revenue,
        employee_size=payload.employee_size,
        description=payload.description,
        linkedin_url=payload.linkedin_url,
        city=payload.city,
    )
    return await repo.add(company)


@router.get("", response_model=Page[CompanyRead], dependencies=[Depends(enforce_rate_limit)])
async def search_companies(
    db: DbSession,
    user: CurrentUser,
    q: str | None = Query(default=None, description="Company name or website"),
    country: str | None = None,
    industry: str | None = None,
    technology: str | None = None,
    erp: str | None = None,
    revenue_min: float | None = None,
    revenue_max: float | None = None,
    employee_size: EmployeeSizeBand | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> Page[CompanyRead]:
    """Search companies by name, website, country, industry, technology, ERP, revenue, size."""
    repo = CompanyRepository(db)
    items, total = await repo.search(
        q=q,
        country=country,
        industry=industry,
        technology=technology,
        erp=erp,
        revenue_min=revenue_min,
        revenue_max=revenue_max,
        employee_size=employee_size,
        page=page,
        page_size=page_size,
    )
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)) if total else 0,
    )


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: str, db: DbSession, user: CurrentUser) -> Company:
    from uuid import UUID

    company = await CompanyRepository(db).get(UUID(company_id))
    if not company:
        raise NotFoundError("Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: str,
    payload: CompanyUpdate,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> Company:
    from uuid import UUID

    repo = CompanyRepository(db)
    company = await repo.get(UUID(company_id))
    if not company:
        raise NotFoundError("Company not found")
    data = payload.model_dump(exclude_unset=True)
    if "website" in data and data["website"]:
        data["website"] = normalize_url(data["website"])
    for key, value in data.items():
        setattr(company, key, value)
    await db.flush()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", response_model=MessageResponse)
async def delete_company(
    company_id: str,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> MessageResponse:
    from uuid import UUID

    repo = CompanyRepository(db)
    company = await repo.get(UUID(company_id))
    if not company:
        raise NotFoundError("Company not found")
    company.is_active = False
    await db.flush()
    return MessageResponse(message="Company archived")
