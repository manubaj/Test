"""
ERP Sales Intelligence Tool — one tool that runs six analysis agents.

Agents (as specified):
  1. Website Intelligence Agent
  2. ERP Opportunity Detection Agent
  3. Technology Detection Agent
  4. Hiring Intelligence Agent
  5. Decision Maker Finder Agent
  6. Lead Scoring Agent

Plus synthesis:
  7. Report Generator Agent

Usage:
  from app.agents.tool import ERPSalesIntelligenceTool
  result = await ERPSalesIntelligenceTool().run(
      company_name="Acme", website="https://example.com"
  )

CLI:
  python -m app.agents --name Acme --website https://example.com
"""

from __future__ import annotations

import json
from typing import Any, Optional

from app.agents.contracts import AgentState, new_state
from app.agents.decision_maker.agent import DecisionMakerAgent
from app.agents.erp_opportunity.agent import ERPOpportunityAgent
from app.agents.hiring_intelligence.agent import HiringIntelligenceAgent
from app.agents.lead_scoring.agent import LeadScoringAgent
from app.agents.report_generator.agent import ReportGeneratorAgent
from app.agents.technology_detection.agent import TechnologyDetectionAgent
from app.agents.website_intelligence.agent import WebsiteIntelligenceAgent
from app.core.logging import get_logger

logger = get_logger(__name__)

# Six primary analysis agents (user-facing)
SIX_AGENTS = (
    ("1_website_intelligence", WebsiteIntelligenceAgent),
    ("2_erp_opportunity", ERPOpportunityAgent),
    ("3_technology_detection", TechnologyDetectionAgent),
    ("4_hiring_intelligence", HiringIntelligenceAgent),
    ("5_decision_maker_finder", DecisionMakerAgent),
    ("6_lead_scoring", LeadScoringAgent),
)


class ERPSalesIntelligenceTool:
    """
    Single multi-agent tool that executes all six intelligence agents
    (and the report synthesizer) and returns a structured JSON result.
    """

    name = "erp_sales_intelligence_tool"
    version = "2.0.0"
    description = (
        "Runs Website Intelligence, ERP Opportunity, Technology Detection, "
        "Hiring Intelligence, Decision Maker Finder, and Lead Scoring agents, "
        "then synthesizes a sales report."
    )

    def __init__(self, *, include_report: bool = True) -> None:
        self.include_report = include_report
        self.agents = [cls() for _, cls in SIX_AGENTS]
        self.report_agent = ReportGeneratorAgent()

    async def run(
        self,
        *,
        company_name: str,
        website: str,
        country: str | None = None,
        industry: str | None = None,
    ) -> dict[str, Any]:
        """Execute the full six-agent pipeline and return a tool result dict."""
        state: AgentState = new_state(
            company_name=company_name,
            website=website,
            country=country,
            industry=industry,
        )

        # Prefer LangGraph when available; otherwise run agents sequentially
        try:
            state = await self._run_langgraph(state)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LangGraph path failed (%s); using sequential tool path", exc)
            state = await self._run_sequential(state)

        return self.format_result(state)

    async def _run_sequential(self, state: AgentState) -> AgentState:
        # Explicit order matches original prompt dependencies
        # 1 website → 3 technology → 2 opportunity → 4 hiring → 5 decision → 6 score → report
        ordered = [
            WebsiteIntelligenceAgent(),
            TechnologyDetectionAgent(),
            ERPOpportunityAgent(),
            HiringIntelligenceAgent(),
            DecisionMakerAgent(),
            LeadScoringAgent(),
        ]
        for agent in ordered:
            state = await agent.run(state)
        if self.include_report:
            state = await self.report_agent.run(state)
        return state

    async def _run_langgraph(self, state: AgentState) -> AgentState:
        from app.agents.workflow.graph import get_workflow

        compiled = get_workflow()
        if not compiled:
            return await self._run_sequential(state)
        result = await compiled.ainvoke(state)
        return result  # type: ignore[return-value]

    def format_result(self, state: AgentState) -> dict[str, Any]:
        """Normalize state into a clear six-agent tool response."""
        tech = state.get("technology_detection") or {
            "technologies": state.get("technologies") or [],
            "erp_stack": [
                t["name"]
                for t in (state.get("technologies") or [])
                if t.get("category") == "erp"
            ],
        }
        dm = state.get("decision_maker_finder") or {
            "decision_makers": state.get("decision_makers") or [],
            "count": len(state.get("decision_makers") or []),
        }

        agents_block = {
            "agent_1_website_intelligence": state.get("website_intelligence"),
            "agent_2_erp_opportunity": state.get("erp_opportunity"),
            "agent_3_technology_detection": tech,
            "agent_4_hiring_intelligence": state.get("hiring_analysis"),
            "agent_5_decision_maker_finder": dm,
            "agent_6_lead_scoring": state.get("lead_score"),
        }

        return {
            "tool": self.name,
            "tool_version": self.version,
            "company_name": state.get("company_name"),
            "website": state.get("website"),
            "agents_completed": [
                t.get("agent_name")
                for t in (state.get("agent_trace") or [])
                if t.get("status") == "completed"
            ],
            "agent_trace": state.get("agent_trace") or [],
            "agents": agents_block,
            "report": state.get("report"),
            "news": state.get("news") or [],
            "errors": state.get("errors") or [],
            # Flat aliases kept for AnalysisService persistence
            "crawl": state.get("crawl"),
            "website_intelligence": state.get("website_intelligence"),
            "technologies": state.get("technologies") or [],
            "erp_opportunity": state.get("erp_opportunity"),
            "hiring_analysis": state.get("hiring_analysis"),
            "decision_makers": state.get("decision_makers") or [],
            "lead_score": state.get("lead_score"),
            "industry": (state.get("website_intelligence") or {}).get("industry")
            or state.get("industry"),
        }

    def list_agents(self) -> list[dict[str, str]]:
        return [
            {
                "id": "1",
                "key": "website_intelligence",
                "name": "Website Intelligence Agent",
                "responsibility": "Crawl site; detect products, ERP, cloud, DB, languages, industry",
            },
            {
                "id": "2",
                "key": "erp_opportunity",
                "name": "ERP Opportunity Detection Agent",
                "responsibility": "Upgrade/migration/expansion signals + confidence",
            },
            {
                "id": "3",
                "key": "technology_detection",
                "name": "Technology Detection Agent",
                "responsibility": "IFS/SAP/Infor/Oracle/Dynamics/cloud/DB/DevOps stack",
            },
            {
                "id": "4",
                "key": "hiring_intelligence",
                "name": "Hiring Intelligence Agent",
                "responsibility": "Careers analysis + hiring score for ERP/cloud roles",
            },
            {
                "id": "5",
                "key": "decision_maker_finder",
                "name": "Decision Maker Finder Agent",
                "responsibility": "CEO/CIO/CTO/VP IT/ERP Manager + profile links",
            },
            {
                "id": "6",
                "key": "lead_scoring",
                "name": "Lead Scoring Agent",
                "responsibility": "0–100 score with weighted factor explanation",
            },
        ]


async def run_sales_intelligence_tool(
    *,
    company_name: str,
    website: str,
    country: Optional[str] = None,
    industry: Optional[str] = None,
) -> dict[str, Any]:
    """Module-level entrypoint used by API / CLI / AnalysisService."""
    tool = ERPSalesIntelligenceTool()
    return await tool.run(
        company_name=company_name,
        website=website,
        country=country,
        industry=industry,
    )


def result_to_json(result: dict[str, Any], *, indent: int = 2) -> str:
    return json.dumps(result, indent=indent, default=str)
