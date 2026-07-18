"""Company persistence and multi-field search."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.enums import EmployeeSizeBand, TechnologyCategory
from app.models.technology import Technology
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    model = Company

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _search_statement(
        self,
        *,
        q: Optional[str] = None,
        country: Optional[str] = None,
        industry: Optional[str] = None,
        technology: Optional[str] = None,
        erp: Optional[str] = None,
        revenue_min: Optional[Decimal] = None,
        revenue_max: Optional[Decimal] = None,
        employee_size: Optional[EmployeeSizeBand] = None,
    ) -> Select:
        stmt = select(Company).where(Company.is_active.is_(True))
        filters = []

        if q:
            like = f"%{q.strip()}%"
            filters.append(or_(Company.name.ilike(like), Company.website.ilike(like)))
        if country:
            filters.append(Company.country.ilike(f"%{country}%"))
        if industry:
            filters.append(Company.industry.ilike(f"%{industry}%"))
        if employee_size:
            filters.append(Company.employee_size == employee_size)
        if revenue_min is not None:
            filters.append(Company.revenue >= revenue_min)
        if revenue_max is not None:
            filters.append(Company.revenue <= revenue_max)

        if technology or erp:
            stmt = stmt.join(Technology, Technology.company_id == Company.id)
            if technology:
                filters.append(Technology.name.ilike(f"%{technology}%"))
            if erp:
                filters.append(
                    and_(
                        Technology.category == TechnologyCategory.ERP,
                        Technology.name.ilike(f"%{erp}%"),
                    )
                )
            stmt = stmt.distinct()

        if filters:
            stmt = stmt.where(and_(*filters))
        return stmt.order_by(Company.name.asc())

    async def search(
        self,
        *,
        q: Optional[str] = None,
        country: Optional[str] = None,
        industry: Optional[str] = None,
        technology: Optional[str] = None,
        erp: Optional[str] = None,
        revenue_min: Optional[Decimal] = None,
        revenue_max: Optional[Decimal] = None,
        employee_size: Optional[EmployeeSizeBand] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Company], int]:
        stmt = self._search_statement(
            q=q,
            country=country,
            industry=industry,
            technology=technology,
            erp=erp,
            revenue_min=revenue_min,
            revenue_max=revenue_max,
            employee_size=employee_size,
        )
        total = await self.count(stmt)
        items = await self.list(
            offset=(page - 1) * page_size,
            limit=page_size,
            statement=stmt,
        )
        return items, total

    async def get_by_website(self, website: str) -> Optional[Company]:
        result = await self.session.execute(
            select(Company).where(Company.website == website)
        )
        return result.scalar_one_or_none()
