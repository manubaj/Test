"""Unit tests for text/url helpers."""

from __future__ import annotations

from app.utils.text import extract_emails, normalize_url, normalize_whitespace, same_domain


def test_normalize_url_adds_scheme() -> None:
    assert normalize_url("example.com/path").startswith("https://")


def test_same_domain() -> None:
    assert same_domain("https://www.acme.com", "https://acme.com/about")
    assert not same_domain("https://acme.com", "https://other.com")


def test_extract_emails() -> None:
    emails = extract_emails("Reach us at sales@acme.com or ops@acme.com")
    assert "sales@acme.com" in emails


def test_normalize_whitespace() -> None:
    assert normalize_whitespace(" a \n b\t") == "a b"
