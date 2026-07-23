"""
Agent 1 — Website Intelligence Agent

Responsibilities:
- Crawl company website
- Extract text
- Detect products, ERP, cloud providers, databases, programming languages, industry
- Output JSON
"""

from __future__ import annotations

from typing import Any

from app.agents.catalogs import (
    INDUSTRY_KEYWORDS,
    PRODUCT_HINTS,
    PROGRAMMING_LANGUAGES,
    TECHNOLOGY_CATALOG,
)
from app.agents.contracts import AgentState, corpus_text
from app.agents.llm import llm_client
from app.agents.runtime import append_trace, evidence_snippet, find_keyword_hits, timed_agent
from app.core.logging import get_logger
from app.services.crawler.engine import WebsiteCrawler

logger = get_logger(__name__)

AGENT_ID = "agent_1_website_intelligence"
AGENT_NAME = "Website Intelligence Agent"


class WebsiteIntelligenceAgent:
    """Independent Agent 1 — website crawl + firmographic/tech signals."""

    name = AGENT_ID

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            website = (state.get("website") or "").strip()
            if not website:
                meta["status"] = "failed"
                meta["notes"].append("No website URL provided")
                state = append_trace(state, meta)
                errors = list(state.get("errors") or []) + ["website_intelligence: missing website"]
                return {**state, "errors": errors}

            crawler = WebsiteCrawler()
            crawl = await crawler.crawl(website)
            text = crawl.combined_text
            lowered = text.lower()

            erp = self._match_category(lowered, "erp")
            clouds = self._match_category(lowered, "cloud")
            databases = self._match_category(lowered, "database")
            languages = [
                lang.strip()
                for lang in PROGRAMMING_LANGUAGES
                if lang.lower() in lowered
            ]
            products = self._detect_products(text)
            industry = self._detect_industry(text) or state.get("industry")

            payload: dict[str, Any] = {
                "agent": AGENT_NAME,
                "company_name": state.get("company_name"),
                "website": website,
                "crawl_success": crawl.success,
                "pages_crawled": len(crawl.pages),
                "products": products,
                "erp_detected": erp,
                "cloud_providers": clouds,
                "databases": databases,
                "programming_languages": languages,
                "industry": industry,
                "page_titles": [p.title for p in crawl.pages if p.title],
                "careers_urls": crawl.careers_urls,
                "about_signals": find_keyword_hits(
                    text, ("about us", "who we are", "our company", "our story")
                ),
                "summary": None,
                "evidence": {
                    "erp": [evidence_snippet(text, e) for e in erp[:3]],
                    "cloud": [evidence_snippet(text, c) for c in clouds[:3]],
                },
            }

            llm_text = await llm_client.complete(
                (
                    "You are Agent 1 Website Intelligence. "
                    "Summarize this company for an ERP sales team in 3 bullets "
                    "(industry, products, tech hints). Text:\n"
                    + text[:7000]
                ),
                system="Return plain text bullets only.",
            )
            if llm_text:
                payload["summary"] = llm_text.strip()
                meta["notes"].append("LLM summary attached")
            else:
                payload["summary"] = self._fallback_summary(payload)
                meta["notes"].append("Heuristic summary (LLM unavailable)")

            news = [
                {
                    "title": url.rsplit("/", 1)[-1].replace("-", " ").title() or url,
                    "url": url,
                    "source": "website_link",
                }
                for url in crawl.news_urls[:12]
            ]

            errors = list(state.get("errors") or [])
            if crawl.error_message:
                errors.append(f"crawl: {crawl.error_message}")
                meta["notes"].append(crawl.error_message)

            state = {
                **state,
                "crawl": crawl.to_dict(),
                "website_intelligence": payload,
                "industry": industry,
                "news": news,
                "errors": errors,
            }
            state = append_trace(state, meta)
            logger.info(
                "%s done pages=%s erp=%s industry=%s",
                AGENT_NAME,
                len(crawl.pages),
                erp,
                industry,
            )
            return state

    def _match_category(self, lowered: str, category: str) -> list[str]:
        found: list[str] = []
        for name, cat, aliases in TECHNOLOGY_CATALOG:
            if cat != category:
                continue
            if name.lower() in lowered or any(a in lowered for a in aliases):
                found.append(name)
        return found

    def _detect_products(self, text: str) -> list[str]:
        products: list[str] = []
        for line in text.split("."):
            low = line.lower()
            if any(h in low for h in PRODUCT_HINTS) and 24 < len(line) < 180:
                cleaned = line.strip()
                if cleaned and cleaned not in products:
                    products.append(cleaned)
            if len(products) >= 8:
                break
        if not products:
            hits = find_keyword_hits(text, PRODUCT_HINTS)
            if hits:
                products = [f"Site mentions: {', '.join(hits[:4])}"]
        return products

    def _detect_industry(self, text: str) -> str | None:
        lowered = text.lower()
        best: tuple[str, int] | None = None
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lowered)
            if score and (best is None or score > best[1]):
                best = (industry, score)
        return best[0] if best else None

    def _fallback_summary(self, payload: dict[str, Any]) -> str:
        bits = [
            f"Company site crawled ({payload.get('pages_crawled') or 0} pages).",
            f"Industry: {payload.get('industry') or 'unspecified'}.",
            f"ERP hints: {', '.join(payload.get('erp_detected') or []) or 'none'}.",
            f"Cloud: {', '.join(payload.get('cloud_providers') or []) or 'none'}.",
        ]
        return " ".join(bits)


async def website_intelligence_node(state: AgentState) -> AgentState:
    return await WebsiteIntelligenceAgent().run(state)
