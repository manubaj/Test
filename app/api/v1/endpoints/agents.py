"""Multi-agent tool endpoints — list and run all six agents."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, enforce_rate_limit, require_roles
from app.agents.tool import ERPSalesIntelligenceTool, run_sales_intelligence_tool
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/agents", tags=["AI Agents"])


class AgentRunRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    website: str = Field(min_length=3, max_length=500)
    country: str | None = None
    industry: str | None = None


@router.get("")
async def list_agents(user: CurrentUser) -> dict:
    """Describe the six analysis agents in the unified tool."""
    tool = ERPSalesIntelligenceTool()
    return {
        "tool": tool.name,
        "version": tool.version,
        "description": tool.description,
        "agents": tool.list_agents(),
        "report_agent": "Report Generator Agent (synthesis)",
    }


@router.post("/run", dependencies=[Depends(enforce_rate_limit)])
async def run_agents(
    payload: AgentRunRequest,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> dict:
    """
    Run all six agents as one tool (does not require a saved company row).

    Returns structured JSON with agent_1 … agent_6 outputs + report.
    """
    return await run_sales_intelligence_tool(
        company_name=payload.company_name,
        website=payload.website,
        country=payload.country,
        industry=payload.industry,
    )
