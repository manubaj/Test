"""
LLM client abstraction with Ollama (default) and OpenAI backends.

Switch providers via ``LLM_PROVIDER`` in .env — no code changes required.
When the remote model is unreachable, callers receive None and agents fall
back to deterministic heuristic analysis (keeps the platform runnable offline).
"""

from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Thin async client for chat completions."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def provider(self) -> str:
        return self.settings.llm_provider

    async def complete(
        self,
        prompt: str,
        *,
        system: str = "You are an ERP sales intelligence analyst. Reply in concise JSON when asked.",
        temperature: float = 0.2,
    ) -> Optional[str]:
        """Return model text or None if the provider is unavailable."""
        try:
            if self.provider == "openai":
                return await self._openai_complete(prompt, system=system, temperature=temperature)
            return await self._ollama_complete(prompt, system=system, temperature=temperature)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM completion failed (%s): %s", self.provider, exc)
            return None

    async def _ollama_complete(
        self, prompt: str, *, system: str, temperature: float
    ) -> Optional[str]:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code >= 400:
                logger.warning("Ollama HTTP %s: %s", response.status_code, response.text[:300])
                return None
            data = response.json()
            return (data.get("message") or {}).get("content")

    async def _openai_complete(
        self, prompt: str, *, system: str, temperature: float
    ) -> Optional[str]:
        if not self.settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured")
            return None
        url = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.openai_model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                logger.warning("OpenAI HTTP %s: %s", response.status_code, response.text[:300])
                return None
            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                return None
            return choices[0]["message"]["content"]


llm_client = LLMClient()
