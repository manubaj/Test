#!/usr/bin/env bash
# Quick login diagnostics for Linux/Docker.
# Usage: ./scripts/diagnose-login.sh

set -euo pipefail

echo "== Container status =="
docker compose ps || true

echo ""
echo "== Backend health =="
curl -sS http://127.0.0.1:8000/api/v1/health || echo "BACKEND UNREACHABLE on :8000"

echo ""
echo "== Login via backend :8000 =="
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin123!"}' || true

echo ""
echo "== Login via frontend proxy :3000 =="
curl -sS -X POST http://127.0.0.1:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin123!"}' || true

echo ""
echo "Credentials: admin@example.com / Admin123!"
echo "If login works in curl but not browser, hard-refresh (Ctrl+Shift+R) after rebuild."
