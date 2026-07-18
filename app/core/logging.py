"""
Structured logging configuration.

Uses stdlib logging with JSON-friendly key=value formatting so Docker
log aggregators can parse messages without extra dependencies.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", app_name: str = "aisales") -> None:
    """Configure root logger once at application startup."""
    root = logging.getLogger()
    if root.handlers:
        # Avoid duplicate handlers when reloaders call setup twice
        root.setLevel(level.upper())
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            f"app={app_name} | %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger for a module."""
    return logging.getLogger(name or "aisales")
