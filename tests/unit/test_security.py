"""Unit tests for password hashing and JWT helpers."""

from __future__ import annotations

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-characters")

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_api_key,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("Admin123!")
    assert hashed != "Admin123!"
    assert verify_password("Admin123!", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip() -> None:
    token = create_access_token("11111111-1111-1111-1111-111111111111", role="admin")
    payload = decode_access_token(token)
    assert payload["role"] == "admin"
    assert payload["sub"] == "11111111-1111-1111-1111-111111111111"


def test_api_key_hash_stable() -> None:
    assert hash_api_key("abc") == hash_api_key("abc")
    assert hash_api_key("abc") != hash_api_key("xyz")
