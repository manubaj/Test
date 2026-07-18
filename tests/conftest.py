"""Shared pytest configuration."""

from __future__ import annotations

import os

# Ensure deterministic settings for unit/integration imports
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-characters")
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("BOOTSTRAP_ADMIN_PASSWORD", "Admin123!")
