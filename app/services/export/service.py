"""CSV and Excel export services for company intelligence."""

from __future__ import annotations

import csv
import io
from typing import Any
from uuid import UUID

from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    CompanyRepository,
    ContactRepository,
    LeadScoreRepository,
    ReportRepository,
    TechnologyRepository,
)


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.companies = CompanyRepository(session)
        self.contacts = ContactRepository(session)
        self.technologies = TechnologyRepository(session)
        self.scores = LeadScoreRepository(session)
        self.reports = ReportRepository(session)

    async def company_rows(self, company_ids: list[UUID] | None = None) -> list[dict[str, Any]]:
        if company_ids:
            companies = []
            for cid in company_ids:
                company = await self.companies.get(cid)
                if company:
                    companies.append(company)
        else:
            companies, _ = await self.companies.search(page=1, page_size=1000)

        rows: list[dict[str, Any]] = []
        for company in companies:
            techs = await self.technologies.for_company(company.id)
            score = await self.scores.latest_for_company(company.id)
            report = await self.reports.latest_for_company(company.id)
            contacts = await self.contacts.for_company(company.id)
            rows.append(
                {
                    "company_id": str(company.id),
                    "name": company.name,
                    "website": company.website or "",
                    "country": company.country or "",
                    "industry": company.industry or "",
                    "revenue": str(company.revenue) if company.revenue is not None else "",
                    "employee_size": (
                        company.employee_size.value if company.employee_size else ""
                    ),
                    "technologies": "; ".join(t.name for t in techs),
                    "lead_score": str(score.score) if score else "",
                    "priority": report.priority.value if report else "",
                    "recommended_services": (
                        "; ".join(report.recommended_services)
                        if report and isinstance(report.recommended_services, list)
                        else ""
                    ),
                    "decision_makers": "; ".join(
                        f"{c.full_name} ({c.role_category.value})" for c in contacts
                    ),
                }
            )
        return rows

    async def export_csv(self, company_ids: list[UUID] | None = None) -> bytes:
        rows = await self.company_rows(company_ids)
        buffer = io.StringIO()
        fieldnames = list(rows[0].keys()) if rows else [
            "company_id",
            "name",
            "website",
            "country",
            "industry",
            "lead_score",
        ]
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return buffer.getvalue().encode("utf-8")

    async def export_excel(self, company_ids: list[UUID] | None = None) -> bytes:
        rows = await self.company_rows(company_ids)
        wb = Workbook()
        ws = wb.active
        ws.title = "Leads"
        headers = list(rows[0].keys()) if rows else ["name", "website", "lead_score"]
        ws.append(headers)
        for row in rows:
            ws.append([row.get(h, "") for h in headers])
        stream = io.BytesIO()
        wb.save(stream)
        return stream.getvalue()
