"""
LangGraph multi-agent workflow.

Pipeline:
1. Website Intelligence
2. Technology Detection
3. ERP Opportunity Detection
4. Hiring Intelligence
5. Decision Maker Finder
6. Lead Scoring
7. Report Generator

If LangGraph is unavailable, a sequential async fallback runs the same nodes.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState
from app.agents.decision_maker.agent import decision_maker_node
from app.agents.erp_opportunity.agent import erp_opportunity_node
from app.agents.hiring_intelligence.agent import hiring_intelligence_node
from app.agents.lead_scoring.agent import lead_scoring_node
from app.agents.report_generator.agent import report_generator_node
from app.agents.technology_detection.agent import technology_detection_node
from app.agents.website_intelligence.agent import website_intelligence_node
from app.core.logging import get_logger

logger = get_logger(__name__)


def _build_langgraph():
    """Compile a LangGraph StateGraph when the library is installed."""
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentState)
    graph.add_node("website_intelligence", website_intelligence_node)
    graph.add_node("technology_detection", technology_detection_node)
    graph.add_node("erp_opportunity", erp_opportunity_node)
    graph.add_node("hiring_intelligence", hiring_intelligence_node)
    graph.add_node("decision_maker", decision_maker_node)
    graph.add_node("lead_scoring", lead_scoring_node)
    graph.add_node("report_generator", report_generator_node)

    graph.set_entry_point("website_intelligence")
    graph.add_edge("website_intelligence", "technology_detection")
    graph.add_edge("technology_detection", "erp_opportunity")
    graph.add_edge("erp_opportunity", "hiring_intelligence")
    graph.add_edge("hiring_intelligence", "decision_maker")
    graph.add_edge("decision_maker", "lead_scoring")
    graph.add_edge("lead_scoring", "report_generator")
    graph.add_edge("report_generator", END)
    return graph.compile()


_compiled = None


def get_workflow():
    """Lazy-compile LangGraph workflow (or None if package missing)."""
    global _compiled
    if _compiled is not None:
        return _compiled
    try:
        _compiled = _build_langgraph()
        logger.info("LangGraph workflow compiled")
    except Exception as exc:  # noqa: BLE001
        logger.warning("LangGraph unavailable, using sequential fallback: %s", exc)
        _compiled = False
    return _compiled


async def run_analysis_workflow(
    *,
    company_name: str,
    website: str,
    country: str | None = None,
    industry: str | None = None,
) -> AgentState:
    """Execute the full intelligence pipeline for one company."""
    initial: AgentState = {
        "company_name": company_name,
        "website": website,
        "country": country,
        "industry": industry,
        "errors": [],
    }

    compiled = get_workflow()
    if compiled:
        # LangGraph supports async invoke via ainvoke
        result = await compiled.ainvoke(initial)
        return result  # type: ignore[return-value]

    # Sequential fallback — same agent order, no graph runtime required
    state: AgentState = initial
    for node in (
        website_intelligence_node,
        technology_detection_node,
        erp_opportunity_node,
        hiring_intelligence_node,
        decision_maker_node,
        lead_scoring_node,
        report_generator_node,
    ):
        state = await node(state)
    return state


def workflow_result_summary(state: AgentState) -> dict[str, Any]:
    """Compact summary for API responses / logs."""
    return {
        "lead_score": (state.get("lead_score") or {}).get("score"),
        "opportunities": (state.get("erp_opportunity") or {}).get("opportunities"),
        "technologies": [t.get("name") for t in (state.get("technologies") or [])],
        "contacts": len(state.get("decision_makers") or []),
        "errors": state.get("errors") or [],
    }
