"""
Website crawling engine.

Uses httpx + BeautifulSoup for reliable, low-cost crawling that works on
Windows/Linux/macOS without browser binaries. Playwright is attempted as an
optional upgrade when installed for JS-heavy sites.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.logging import get_logger
from app.utils.text import normalize_url, normalize_whitespace, same_domain

logger = get_logger(__name__)


@dataclass
class PageContent:
    """Single crawled page."""

    url: str
    status_code: int
    title: str
    text: str
    links: list[str] = field(default_factory=list)


@dataclass
class CrawlResult:
    """Aggregate crawl output for agent consumption."""

    seed_url: str
    success: bool
    pages: list[PageContent] = field(default_factory=list)
    combined_text: str = ""
    careers_urls: list[str] = field(default_factory=list)
    news_urls: list[str] = field(default_factory=list)
    error_message: Optional[str] = None
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed_url": self.seed_url,
            "success": self.success,
            "pages_crawled": len(self.pages),
            "combined_text": self.combined_text[:50000],
            "careers_urls": self.careers_urls,
            "news_urls": self.news_urls,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "page_titles": [p.title for p in self.pages],
            "metadata": self.metadata,
        }


class WebsiteCrawler:
    """Breadth-first same-domain crawler with careers/news prioritization."""

    CAREERS_HINTS = ("career", "careers", "jobs", "join-us", "work-with-us", "vacancies")
    NEWS_HINTS = ("news", "press", "media", "blog", "insights", "about")

    def __init__(self) -> None:
        self.settings = get_settings()

    async def crawl(self, url: str, *, max_pages: Optional[int] = None) -> CrawlResult:
        """Crawl a company website and return extracted text + link sets."""
        seed = normalize_url(url)
        started = time.perf_counter()
        max_pages = max_pages or self.settings.crawler_max_pages
        result = CrawlResult(seed_url=seed, success=False)

        if not seed:
            result.error_message = "Empty URL"
            return result

        try:
            pages = await self._crawl_httpx(seed, max_pages=max_pages)
            if not pages:
                # Optional Playwright fallback for JS-rendered sites
                pages = await self._crawl_playwright(seed, max_pages=min(3, max_pages))
                result.metadata["engine"] = "playwright" if pages else "httpx"
            else:
                result.metadata["engine"] = "httpx"

            result.pages = pages
            texts = [p.text for p in pages if p.text]
            result.combined_text = normalize_whitespace("\n\n".join(texts))
            all_links = {link for p in pages for link in p.links}
            result.careers_urls = sorted(
                link for link in all_links if any(h in link.lower() for h in self.CAREERS_HINTS)
            )
            result.news_urls = sorted(
                link for link in all_links if any(h in link.lower() for h in self.NEWS_HINTS)
            )[:20]
            result.success = bool(result.combined_text)
            if not result.success:
                result.error_message = "No extractable text found"
        except Exception as exc:  # noqa: BLE001 — surfaced to crawl_logs
            logger.exception("Crawl failed for %s", seed)
            result.error_message = str(exc)
        finally:
            result.duration_ms = int((time.perf_counter() - started) * 1000)

        return result

    async def _crawl_httpx(self, seed: str, *, max_pages: int) -> list[PageContent]:
        headers = {"User-Agent": self.settings.crawler_user_agent}
        timeout = httpx.Timeout(self.settings.crawler_timeout_seconds)
        visited: set[str] = set()
        queue: list[str] = [seed]
        pages: list[PageContent] = []

        async with httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            while queue and len(pages) < max_pages:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                try:
                    response = await client.get(current)
                except httpx.HTTPError as exc:
                    logger.warning("HTTP error crawling %s: %s", current, exc)
                    continue

                content_type = response.headers.get("content-type", "")
                if "html" not in content_type.lower() and current != seed:
                    continue

                page = self._parse_html(current, response.status_code, response.text)
                pages.append(page)

                # Prioritize careers/about/news links in the BFS queue
                prioritized, normal = [], []
                for link in page.links:
                    if link in visited:
                        continue
                    low = link.lower()
                    if any(h in low for h in self.CAREERS_HINTS + self.NEWS_HINTS + ("about",)):
                        prioritized.append(link)
                    else:
                        normal.append(link)
                queue.extend(prioritized + normal)

        return pages

    async def _crawl_playwright(self, seed: str, *, max_pages: int) -> list[PageContent]:
        """Best-effort Playwright path; returns [] if Playwright is unavailable."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.info("Playwright not installed; skipping JS crawl fallback")
            return []

        pages: list[PageContent] = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.settings.crawler_user_agent
                )
                page = await context.new_page()
                await page.goto(seed, wait_until="domcontentloaded", timeout=30000)
                html = await page.content()
                pages.append(self._parse_html(seed, 200, html))
                await browser.close()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Playwright crawl failed: %s", exc)
            return []
        return pages[:max_pages]

    def _parse_html(self, url: str, status_code: int, html: str) -> PageContent:
        soup = BeautifulSoup(html or "", "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        title = normalize_whitespace(soup.title.get_text() if soup.title else "")
        text = normalize_whitespace(soup.get_text(" ", strip=True))
        links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            absolute = normalize_url(urljoin(url, href))
            if absolute and same_domain(url, absolute):
                # Skip binary assets
                path = urlparse(absolute).path.lower()
                if path.endswith((".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".zip")):
                    continue
                links.append(absolute)
        # Deduplicate while preserving order
        unique_links = list(dict.fromkeys(links))
        return PageContent(
            url=url,
            status_code=status_code,
            title=title,
            text=text[:20000],
            links=unique_links,
        )


async def crawl_website(url: str) -> CrawlResult:
    """Module-level convenience wrapper."""
    return await WebsiteCrawler().crawl(url)


if __name__ == "__main__":
    # Manual smoke: python -m app.services.crawler.engine https://example.com
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    data = asyncio.run(crawl_website(target))
    print(data.to_dict())
