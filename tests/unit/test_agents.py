"""Unit tests for the six-agent ERP Sales Intelligence Tool."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.contracts import AgentState
from app.agents.decision_maker.agent import DecisionMakerAgent
from app.agents.erp_opportunity.agent import ERPOpportunityAgent
from app.agents.hiring_intelligence.agent import HiringIntelligenceAgent
from app.agents.lead_scoring.agent import LeadScoringAgent
from app.agents.report_generator.agent import ReportGeneratorAgent
from app.agents.technology_detection.agent import TechnologyDetectionAgent
from app.agents.tool import ERPSalesIntelligenceTool
from app.agents.website_intelligence.agent import WebsiteIntelligenceAgent
from app.services.crawler.engine import CrawlResult, PageContent


SAMPLE_TEXT = """
Acme Manufacturing builds industrial equipment across three factories.
We run IFS Cloud and are planning a cloud migration and digital transformation.
Careers: we are hiring SAP consultants, IFS developers, and DevOps engineers.
Our CIO Jane Smith leads IT. Contact leadership@acme.example.
Expansion includes a new plant in Texas. PostgreSQL and Kubernetes power our stack.
Azure and Docker are used in delivery. About us / products / solutions page.
"""


def _fake_crawl(text: str = SAMPLE_TEXT) -> CrawlResult:
    return CrawlResult(
        seed_url="https://acme.example",
        success=True,
        pages=[
            PageContent(
                url="https://acme.example",
                status_code=200,
                title="Acme Manufacturing",
                text=text,
                links=["https://acme.example/careers", "https://acme.example/news"],
            )
        ],
        combined_text=text,
        careers_urls=["https://acme.example/careers"],
        news_urls=["https://acme.example/news/expansion"],
        duration_ms=12,
    )


@pytest.mark.asyncio
async def test_each_of_six_agents_produces_output() -> None:
    state: AgentState = {
        "company_name": "Acme",
        "website": "https://acme.example",
        "crawl": {"combined_text": SAMPLE_TEXT, "careers_urls": []},
        "website_intelligence": {"industry": "Manufacturing", "erp_detected": ["IFS Cloud"]},
        "errors": [],
        "agent_trace": [],
    }

    state = await TechnologyDetectionAgent().run(state)
    assert state["technology_detection"]["total_detected"] >= 3
    assert "IFS Cloud" in {t["name"] for t in state["technologies"]}

    state = await ERPOpportunityAgent().run(state)
    assert state["erp_opportunity"]["confidence"] >= 40
    assert any("IFS" in o or "SAP" in o for o in state["erp_opportunity"]["opportunities"])

    state = await HiringIntelligenceAgent().run(state)
    assert state["hiring_analysis"]["hiring_score"] >= 20
    assert state["hiring_analysis"]["erp_related_hiring"] is True

    state = await DecisionMakerAgent().run(state)
    assert state["decision_maker_finder"]["count"] >= 1

    state = await LeadScoringAgent().run(state)
    assert state["lead_score"]["score"] >= 50
    assert len(state["lead_score"]["factors"]) >= 2

    state = await ReportGeneratorAgent().run(state)
    assert state["report"]["priority"] in {"low", "medium", "high", "critical"}

    # All six analysis agents (+ report) should appear in trace
    names = [t["agent_name"] for t in state["agent_trace"]]
    assert len(names) >= 6


@pytest.mark.asyncio
async def test_unified_tool_runs_all_six_agents() -> None:
    tool = ERPSalesIntelligenceTool()
    assert len(tool.list_agents()) == 6

    with patch(
        "app.agents.website_intelligence.agent.WebsiteCrawler.crawl",
        new=AsyncMock(return_value=_fake_crawl()),
    ), patch(
        "app.agents.hiring_intelligence.agent.WebsiteCrawler.crawl",
        new=AsyncMock(return_value=_fake_crawl()),
    ), patch(
        "app.agents.workflow.graph.get_workflow",
        return_value=False,
    ):
        result = await tool.run(
            company_name="Acme Manufacturing",
            website="https://acme.example",
            industry="Manufacturing",
        )

    agents: dict[str, Any] = result["agents"]
    assert agents["agent_1_website_intelligence"] is not None
    assert agents["agent_2_erp_opportunity"] is not None
    assert agents["agent_3_technology_detection"] is not None
    assert agents["agent_4_hiring_intelligence"] is not None
    assert agents["agent_5_decision_maker_finder"] is not None
    assert agents["agent_6_lead_scoring"] is not None
    assert result["report"] is not None
    assert result["lead_score"]["score"] >= 40
    completed = result["agents_completed"]
    assert len(completed) >= 6


@pytest.mark.asyncio
async def test_website_intelligence_agent_json_contract() -> None:
    with patch(
        "app.agents.website_intelligence.agent.WebsiteCrawler.crawl",
        new=AsyncMock(return_value=_fake_crawl()),
    ):
        state = await WebsiteIntelligenceAgent().run(
            {
                "company_name": "Acme",
                "website": "https://acme.example",
                "errors": [],
                "agent_trace": [],
            }
        )
    payload = state["website_intelligence"]
    for key in (
        "products",
        "erp_detected",
        "cloud_providers",
        "databases",
        "programming_languages",
        "industry",
        "summary",
    ):
        assert key in payload
