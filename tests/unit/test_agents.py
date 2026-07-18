"""Unit tests for AI agents using mocked crawl text (no LLM/DB required)."""

from __future__ import annotations

import pytest

from app.agents.base import AgentState
from app.agents.erp_opportunity.agent import ERPOpportunityAgent
from app.agents.hiring_intelligence.agent import HiringIntelligenceAgent
from app.agents.lead_scoring.agent import LeadScoringAgent
from app.agents.technology_detection.agent import TechnologyDetectionAgent
from app.agents.decision_maker.agent import DecisionMakerAgent
from app.agents.report_generator.agent import ReportGeneratorAgent


SAMPLE_TEXT = """
Acme Manufacturing builds industrial equipment across three factories.
We run IFS Cloud and are planning a cloud migration and digital transformation.
Careers: we are hiring SAP consultants, IFS developers, and DevOps engineers.
Our CIO Jane Smith leads IT. Contact leadership@acme.example.
Expansion includes a new plant in Texas. PostgreSQL and Kubernetes power our stack.
"""


@pytest.mark.asyncio
async def test_technology_detection_finds_erp_and_cloud() -> None:
    state: AgentState = {
        "company_name": "Acme",
        "website": "https://acme.example",
        "crawl": {"combined_text": SAMPLE_TEXT},
        "website_intelligence": {},
    }
    result = await TechnologyDetectionAgent().run(state)
    names = {t["name"] for t in result["technologies"]}
    assert "IFS Cloud" in names
    assert "PostgreSQL" in names
    assert "Kubernetes" in names


@pytest.mark.asyncio
async def test_erp_opportunity_and_lead_score() -> None:
    state: AgentState = {
        "company_name": "Acme",
        "website": "https://acme.example",
        "crawl": {"combined_text": SAMPLE_TEXT},
        "technologies": [
            {"name": "IFS Cloud", "category": "erp", "confidence": 90},
            {"name": "SAP S/4HANA", "category": "erp", "confidence": 70},
        ],
        "website_intelligence": {"industry": "Manufacturing"},
    }
    state = await ERPOpportunityAgent().run(state)
    assert state["erp_opportunity"]["confidence"] > 40
    assert any("IFS" in o or "SAP" in o for o in state["erp_opportunity"]["opportunities"])

    state = await HiringIntelligenceAgent().run(state)
    assert state["hiring_analysis"]["hiring_score"] >= 20

    state = await LeadScoringAgent().run(state)
    assert 0 <= state["lead_score"]["score"] <= 100
    assert state["lead_score"]["score"] >= 50


@pytest.mark.asyncio
async def test_decision_maker_and_report() -> None:
    state: AgentState = {
        "company_name": "Acme Manufacturing",
        "website": "https://acme.example",
        "crawl": {"combined_text": SAMPLE_TEXT},
        "technologies": [{"name": "IFS Cloud", "category": "erp"}],
        "erp_opportunity": {
            "opportunities": ["IFS Cloud Migration"],
            "signals": {"cloud_migration": {"matched": ["cloud migration"]}},
            "confidence": 70,
        },
        "hiring_analysis": {"hiring_score": 40, "categories": {"IFS": ["ifs"]}},
        "website_intelligence": {"industry": "Manufacturing"},
        "lead_score": {
            "score": 70,
            "explanation": "ERP Detected (+30); Hiring ERP (+20)",
            "factors": [],
        },
    }
    state = await DecisionMakerAgent().run(state)
    assert isinstance(state["decision_makers"], list)

    state = await ReportGeneratorAgent().run(state)
    report = state["report"]
    assert report["executive_summary"]
    assert report["priority"] in {"low", "medium", "high", "critical"}
    assert "IFS Cloud Migration" in report["recommended_services"]
