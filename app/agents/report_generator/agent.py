"""
Agent 7 — Report Generator (synthesis step of the multi-agent tool)

Generates: Executive Summary, Business Opportunity, Why prospect,
Recommended services, Estimated deal size, Priority, Next Action.
"""

from __future__ import annotations

from typing import Any

from app.agents.contracts import AgentState
from app.agents.llm import llm_client
from app.agents.runtime import append_trace, timed_agent
from app.core.logging import get_logger

logger = get_logger(__name__)

AGENT_ID = "agent_7_report_generator"
AGENT_NAME = "Report Generator Agent"


class ReportGeneratorAgent:
    name = AGENT_ID

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            company = state.get("company_name") or "Target company"
            opportunity = state.get("erp_opportunity") or {}
            opportunities = opportunity.get("opportunities") or [
                "ERP Digital Transformation"
            ]
            score = int((state.get("lead_score") or {}).get("score") or 0)
            hiring_score = int(
                (state.get("hiring_analysis") or {}).get("hiring_score") or 0
            )
            techs = [t["name"] for t in (state.get("technologies") or [])]
            industry = (state.get("website_intelligence") or {}).get("industry") or state.get(
                "industry"
            )
            contacts = state.get("decision_makers") or []

            if score >= 80:
                deal_label, deal_size, priority = "250k-500k", 375000, "critical"
            elif score >= 60:
                deal_label, deal_size, priority = "100k-250k", 175000, "high"
            elif score >= 40:
                deal_label, deal_size, priority = "50k-100k", 75000, "medium"
            else:
                deal_label, deal_size, priority = "25k-50k", 35000, "low"

            contact_line = (
                ", ".join(
                    f"{c.get('full_name')} ({c.get('title')})"
                    for c in contacts[:3]
                    if c.get("full_name")
                )
                or "IT / executive leadership (to be confirmed)"
            )

            executive_summary = (
                f"{company} is a {priority}-priority ERP prospect "
                f"(lead score {score}/100). Detected stack: "
                f"{', '.join(techs) if techs else 'not conclusively identified'}. "
                f"Primary opportunities: {', '.join(opportunities)}. "
                f"Industry: {industry or 'unspecified'}."
            )
            business_opportunity = (
                f"Signals indicate demand for {', '.join(opportunities)}. "
                f"Hiring score {hiring_score}/100. "
                f"Opportunity confidence "
                f"{(opportunity.get('confidence') or 0)}/100."
            )
            why_prospect = (state.get("lead_score") or {}).get("explanation") or (
                "Firmographic and technology signals suggest ERP modernization potential."
            )
            next_action = (
                f"Engage {contact_line} with a discovery call focused on "
                f"{opportunities[0]}; validate roadmap and propose a capability workshop."
            )

            report: dict[str, Any] = {
                "agent": AGENT_NAME,
                "executive_summary": executive_summary,
                "business_opportunity": business_opportunity,
                "why_prospect": why_prospect,
                "recommended_services": opportunities,
                "estimated_deal_size": deal_size,
                "estimated_deal_size_label": deal_label,
                "priority": priority,
                "next_action": next_action,
                "stakeholders": contacts[:5],
            }

            polished = await llm_client.complete(
                "Rewrite this executive summary for a sales VP in 3 sentences:\n"
                + executive_summary
            )
            if polished:
                report["executive_summary"] = polished.strip()
                report["full_content"] = {"llm_polished": True}
                meta["notes"].append("LLM-polished executive summary")
            else:
                report["full_content"] = {"llm_polished": False}

            state = {**state, "report": report}
            return append_trace(state, meta)


async def report_generator_node(state: AgentState) -> AgentState:
    return await ReportGeneratorAgent().run(state)
