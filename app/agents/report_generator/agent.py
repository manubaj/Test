"""
Agent 7 — Report Generator.

Produces executive summary, opportunity narrative, recommended services,
estimated deal size, priority, and next action.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState
from app.agents.llm import llm_client
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportGeneratorAgent:
    name = "report_generator"

    async def run(self, state: AgentState) -> AgentState:
        company = state.get("company_name") or "Target company"
        opportunity = state.get("erp_opportunity") or {}
        opportunities = opportunity.get("opportunities") or ["ERP Digital Transformation"]
        score = (state.get("lead_score") or {}).get("score") or 0
        hiring_score = (state.get("hiring_analysis") or {}).get("hiring_score") or 0
        techs = [t["name"] for t in (state.get("technologies") or [])]
        industry = (state.get("website_intelligence") or {}).get("industry") or state.get(
            "industry"
        )

        # Deal size heuristic by score band
        if score >= 80:
            deal_label, deal_size, priority = "250k-500k", 375000, "critical"
        elif score >= 60:
            deal_label, deal_size, priority = "100k-250k", 175000, "high"
        elif score >= 40:
            deal_label, deal_size, priority = "50k-100k", 75000, "medium"
        else:
            deal_label, deal_size, priority = "25k-50k", 35000, "low"

        executive_summary = (
            f"{company} presents a {priority} ERP opportunity "
            f"(lead score {score}/100). Detected stack: "
            f"{', '.join(techs) if techs else 'not conclusively identified'}. "
            f"Primary opportunities: {', '.join(opportunities)}."
        )
        business_opportunity = (
            f"Signals indicate potential demand for {', '.join(opportunities)}. "
            f"Industry context: {industry or 'unspecified'}. "
            f"Hiring score: {hiring_score}/100."
        )
        why_prospect = (state.get("lead_score") or {}).get("explanation") or (
            "Firmographic and technology signals suggest ERP modernization potential."
        )
        next_action = (
            "Book an discovery call with CIO/IT Director; validate ERP roadmap and "
            "share a tailored capability deck for "
            f"{opportunities[0]}."
        )

        report: dict[str, Any] = {
            "executive_summary": executive_summary,
            "business_opportunity": business_opportunity,
            "why_prospect": why_prospect,
            "recommended_services": opportunities,
            "estimated_deal_size": deal_size,
            "estimated_deal_size_label": deal_label,
            "priority": priority,
            "next_action": next_action,
        }

        # Optional LLM polish
        polished = await llm_client.complete(
            "Rewrite this executive summary for a sales VP in 3 sentences:\n"
            + executive_summary
        )
        if polished:
            report["executive_summary"] = polished.strip()
            report["full_content"] = {"llm_polished": True}

        return {**state, "report": report}


async def report_generator_node(state: AgentState) -> AgentState:
    return await ReportGeneratorAgent().run(state)
