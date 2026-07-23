"""Public web search helpers for LinkedIn-indexed jobs and ERP demand signals."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.logging import get_logger
from app.utils.text import normalize_whitespace

logger = get_logger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (compatible; AISalesIntelligenceBot/2.0; +https://localhost) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class SearchHit:
    title: str
    url: str
    snippet: str
    source: str = "web"
    offering_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "offering_key": self.offering_key,
        }


@dataclass
class SearchBatch:
    query: str
    offering_key: str
    hits: list[SearchHit] = field(default_factory=list)
    error: str | None = None


class PublicWebSearch:
    """
    Discover publicly indexed pages (including LinkedIn jobs) via DuckDuckGo HTML.

    Note: Direct authenticated LinkedIn scraping is not used (ToS / blocking).
    We discover LinkedIn URLs that search engines have indexed, then enrich via
    the company's own website.
    """

    async def search(
        self,
        query: str,
        *,
        offering_key: str,
        max_results: int = 10,
    ) -> SearchBatch:
        batch = SearchBatch(query=query, offering_key=offering_key)
        try:
            hits = await self._duckduckgo(query, max_results=max_results)
            if not hits:
                hits = await self._bing(query, max_results=max_results)
            for hit in hits:
                hit.offering_key = offering_key
                if "linkedin.com" in hit.url.lower():
                    hit.source = "linkedin_indexed"
            batch.hits = hits
        except Exception as exc:  # noqa: BLE001
            logger.warning("Search failed for %s: %s", query, exc)
            batch.error = str(exc)
        return batch

    async def _duckduckgo(self, query: str, *, max_results: int) -> list[SearchHit]:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": USER_AGENT}
        async with httpx.AsyncClient(headers=headers, timeout=25.0, follow_redirects=True) as client:
            response = await client.post(url, data={"q": query})
            if response.status_code >= 400:
                return []
            soup = BeautifulSoup(response.text, "html.parser")
            hits: list[SearchHit] = []
            for result in soup.select(".result"):
                anchor = result.select_one("a.result__a")
                snippet_el = result.select_one(".result__snippet")
                if not anchor or not anchor.get("href"):
                    continue
                href = self._clean_ddg_url(anchor["href"])
                if not href:
                    continue
                hits.append(
                    SearchHit(
                        title=normalize_whitespace(anchor.get_text(" ", strip=True)),
                        url=href,
                        snippet=normalize_whitespace(
                            snippet_el.get_text(" ", strip=True) if snippet_el else ""
                        ),
                        source="duckduckgo",
                    )
                )
                if len(hits) >= max_results:
                    break
            return hits

    async def _bing(self, query: str, *, max_results: int) -> list[SearchHit]:
        url = "https://www.bing.com/search"
        headers = {"User-Agent": USER_AGENT}
        async with httpx.AsyncClient(headers=headers, timeout=25.0, follow_redirects=True) as client:
            response = await client.get(url, params={"q": query, "count": max_results})
            if response.status_code >= 400:
                return []
            soup = BeautifulSoup(response.text, "html.parser")
            hits: list[SearchHit] = []
            for li in soup.select("li.b_algo"):
                anchor = li.select_one("h2 a")
                snippet_el = li.select_one(".b_caption p")
                if not anchor or not anchor.get("href"):
                    continue
                hits.append(
                    SearchHit(
                        title=normalize_whitespace(anchor.get_text(" ", strip=True)),
                        url=anchor["href"],
                        snippet=normalize_whitespace(
                            snippet_el.get_text(" ", strip=True) if snippet_el else ""
                        ),
                        source="bing",
                    )
                )
                if len(hits) >= max_results:
                    break
            return hits

    def _clean_ddg_url(self, href: str) -> str:
        # DuckDuckGo wraps redirects: /l/?uddg=<url>
        if "uddg=" in href:
            qs = parse_qs(urlparse(href).query)
            if "uddg" in qs:
                return unquote(qs["uddg"][0])
        if href.startswith("http"):
            return href
        return ""


_COMPANY_STOP = re.compile(
    r"\b(hiring|jobs?|careers?|linkedin|salary|remote|apply|recruit)\b",
    re.I,
)


def infer_company_name(title: str, snippet: str = "") -> str | None:
    """Best-effort company name from a job/search title."""
    text = title or ""
    # Patterns: "SAP Consultant at Acme Corp" / "Acme Corp hiring IFS"
    m = re.search(r"\bat\s+([A-Z][\w&.,'\- ]{2,60})$", text.strip())
    if m and not _COMPANY_STOP.search(m.group(1)):
        return m.group(1).strip(" -|")
    m = re.search(r"^([A-Z][\w&.,'\- ]{2,60})\s+is hiring", text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"^([A-Z][\w&.,'\- ]{2,40})\s+[-–|]", text)
    if m and not _COMPANY_STOP.search(m.group(1)):
        return m.group(1).strip()
    # LinkedIn job titles often end with " | Company"
    if "|" in text:
        part = text.split("|")[-1].strip()
        if 2 < len(part) < 80 and not _COMPANY_STOP.search(part):
            return part
    return None


def extract_linkedin_company_url(url: str) -> str | None:
    if "linkedin.com/company/" in url.lower():
        return url.split("?")[0].rstrip("/")
    return None
