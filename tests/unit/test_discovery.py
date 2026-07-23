"""Tests for ERP demand discovery pipeline (mocked search/crawl)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.discovery.pipeline import (
    DemandDiscoveryAgent,
    ERPDemandConfirmationAgent,
    ERPDiscoveryTool,
    HiringSignalAgent,
    LeadRankingAgent,
    DecisionMakerContactAgent,
)
from app.agents.erp_catalog import ERP_OFFERINGS, all_offerings
from app.services.search.web_search import SearchBatch, SearchHit, infer_company_name


def test_hardcoded_offerings_cover_major_erps() -> None:
    labels = {o.label for o in ERP_OFFERINGS}
    assert "IFS Implementation" in labels
    assert "SAP S/4HANA Migration" in labels
    assert "Oracle ERP Migration" in labels
    assert "Infor LN Upgrade" in labels
    assert "Dynamics 365 Implementation" in labels
    assert len(all_offerings()) >= 15


def test_infer_company_name() -> None:
    assert infer_company_name("SAP Consultant at Acme Manufacturing") == "Acme Manufacturing"
    assert infer_company_name("Acme Corp is hiring IFS developers") == "Acme Corp"


@pytest.mark.asyncio
async def test_discovery_agents_produce_ranked_leads() -> None:
    hits = [
        SearchHit(
            title="IFS Cloud Consultant at Globex Industrial",
            url="https://www.linkedin.com/jobs/view/123",
            snippet="Globex is hiring for IFS Cloud migration in Germany",
            source="linkedin_indexed",
            offering_key="ifs_cloud_migration",
        ),
        SearchHit(
            title="S/4HANA migration RFP - Globex Industrial",
            url="https://www.globex-industrial.example/careers",
            snippet="We are migrating from ECC to SAP S/4HANA",
            source="web",
            offering_key="sap_s4_migration",
        ),
    ]

    async def fake_search(query, *, offering_key, max_results=10):
        return SearchBatch(query=query, offering_key=offering_key, hits=hits)

    site_text = """
    Globex Industrial is a manufacturing company headquartered in Munich, Germany.
    CIO Anna Weber leads IT. Contact anna.weber@globex-industrial.example
    Phone +49 89 12345678. We are hiring SAP consultants and IFS developers.
    """

    class FakeCrawl:
        success = True
        pages = [object()]
        combined_text = site_text
        careers_urls = ["https://www.globex-industrial.example/careers"]
        news_urls = []
        error_message = None

    with patch(
        "app.agents.discovery.pipeline.PublicWebSearch.search",
        new=AsyncMock(side_effect=fake_search),
    ), patch(
        "app.agents.discovery.pipeline.WebsiteCrawler.crawl",
        new=AsyncMock(return_value=FakeCrawl()),
    ), patch(
        "app.agents.discovery.pipeline.default_discovery_queries",
        return_value=[("ifs_cloud_migration", 'site:linkedin.com/jobs "IFS Cloud"')],
    ):
        tool = ERPDiscoveryTool(target_lead_count=100)
        assert len(tool.list_agents()) == 6
        result = await tool.run()

    assert result["leads_found"] >= 1
    lead = result["leads"][0]
    assert "Globex" in lead["company_name"]
    assert lead["decision_makers"]
    assert any(
        (p.get("email") or "").endswith("globex-industrial.example")
        or p.get("phone")
        for p in lead["decision_makers"]
    )
    assert len(result["agent_trace"]) == 6
