"""Company schemas including multi-field search filters."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import EmployeeSizeBand
from app.schemas.common import ORMModel


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    website: Optional[str] = Field(default=None, max_length=500)
    country: Optional[str] = Field(default=None, max_length=100)
    industry: Optional[str] = Field(default=None, max_length=150)
    revenue: Optional[Decimal] = None
    employee_size: Optional[EmployeeSizeBand] = None
    description: Optional[str] = None
    linkedin_url: Optional[str] = None
    city: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    website: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    revenue: Optional[Decimal] = None
    employee_size: Optional[EmployeeSizeBand] = None
    description: Optional[str] = None
    linkedin_url: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyRead(ORMModel):
    id: UUID
    name: str
    website: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    revenue: Optional[Decimal] = None
    employee_size: Optional[EmployeeSizeBand] = None
    description: Optional[str] = None
    linkedin_url: Optional[str] = None
    city: Optional[str] = None
    is_active: bool


class CompanySearchFilters(BaseModel):
    """Search by name, website, country, industry, technology, ERP, revenue, size."""

    q: Optional[str] = Field(default=None, description="Company name or website")
    country: Optional[str] = None
    industry: Optional[str] = None
    technology: Optional[str] = None
    erp: Optional[str] = None
    revenue_min: Optional[Decimal] = None
    revenue_max: Optional[Decimal] = None
    employee_size: Optional[EmployeeSizeBand] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
