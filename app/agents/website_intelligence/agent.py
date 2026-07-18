"""
Agent 1 — Website Intelligence Agent.

Crawls the company website, extracts text, and detects products, ERP signals,
cloud providers, databases, programming languages, and industry.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState, find_keyword_hits
from app.agents.catalogs import (
    INDUSTRY_KEYWORDS,
    PRODUCT_HINTS,
    PROGRAMMING_LANGUAGES,
    TECHNOLOGY_CATALOG,
)
from app.agents.llm import llm_client
from app.core.logging import get_logger
from app.services.crawler.engine import WebsiteCrawler

logger = get_logger(__name__)


class WebsiteIntelligenceAgent:
    """Independent website intelligence agent."""

    name = "website_intelligence"

    async def run(self, state: AgentState) -> AgentState:
        website = state.get("website") or ""
        crawler = WebsiteCrawler()
        crawl = await crawler.crawl(website)
        text = crawl.combined_text
        lowered = text.lower()

        products = self._detect_products(text)
        erp = [
            name
            for name, category, aliases in TECHNOLOGY_CATALOG
            if category == "erp"
            and (name.lower() in lowered or any(a in lowered for a in aliases))
        ]
        clouds = [
            name
            for name, category, aliases in TECHNOLOGY_CATALOG
            if category == "cloud"
            and (name.lower() in lowered or any(a in lowered for a in aliases))
        ]
        databases = [
            name
            for name, category, aliases in TECHNOLOGY_CATALOG
            if category == "database"
            and (name.lower() in lowered or any(a in lowered for a in aliases))
        ]
        languages = [
            lang.strip()
            for lang in PROGRAMMING_LANGUAGES
            if lang.lower() in lowered
        ]
        industry = self._detect_industry(text) or state.get("industry")

        payload: dict[str, Any] = {
            "company_name": state.get("company_name"),
            "website": website,
            "products": products,
            "erp_detected": erp,
            "cloud_providers": clouds,
            "databases": databases,
            "programming_languages": languages,
            "industry": industry,
            "page_titles": [p.title for p in crawl.pages],
            "careers_urls": crawl.careers_urls,
            "summary": None,
        }

        # Optional LLM enrichment — ignored if Ollama/OpenAI unavailable
        llm_text = await llm_client.complete(
            "Summarize this company website for ERP sales in 2 sentences:\n"
            + text[:6000]
        )
        if llm_text:
            payload["summary"] = llm_text.strip()

        news = [
            {"title": url.rsplit("/", 1)[-1].replace("-", " ").title(), "url": url}
            for url in crawl.news_urls[:10]
        ]

        errors = list(state.get("errors") or [])
        if crawl.error_message:
            errors.append(f"crawl: {crawl.error_message}")

        return {
            **state,
            "crawl": crawl.to_dict(),
            "website_intelligence": payload,
            "industry": industry,
            "news": news,
            "errors": errors,
        }

    def _detect_products(self, text: str) -> list[str]:
        hits = find_keyword_hits(text, PRODUCT_HINTS)
        # Extract nearby noun-ish phrases after product hint words — keep simple
        products: list[str] = []
        for line in text.split("."):
            low = line.lower()
            if any(h in low for h in PRODUCT_HINTS) and 20 < len(line) < 160:
                products.append(line.strip())
            if len(products) >= 5:
                break
        if hits and not products:
            products = [f"Mentions: {', '.join(hits)}"]
        return products

    def _detect_industry(self, text: str) -> str | None:
        lowered = text.lower()
        best: tuple[str, int] | None = None
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lowered)
            if score and (best is None or score > best[1]):
                best = (industry, score)
        return best[0] if best else None


async def website_intelligence_node(state: AgentState) -> AgentState:
    """LangGraph node wrapper."""
    return await WebsiteIntelligenceAgent().run(state)
