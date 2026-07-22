#!/usr/bin/env bash
# Login diagnostics — run from repo root on the machine where Docker is running.
set -u

echo "======== docker compose ps ========"
docker compose ps || true

echo ""
echo "======== backend logs (last 40) ========"
docker compose logs backend --tail 40 || true

echo ""
echo "======== GET /api/v1/health :8000 ========"
curl -sS -m 5 http://127.0.0.1:8000/api/v1/health || echo FAIL

echo ""
echo "======== GET /api/v1/ready :8000 ========"
curl -sS -m 5 http://127.0.0.1:8000/api/v1/ready || echo FAIL

echo ""
echo "======== GET /api/v1/auth/login-help :8000 ========"
curl -sS -m 5 http://127.0.0.1:8000/api/v1/auth/login-help || echo FAIL

echo ""
echo "======== POST login via :8000 ========"
curl -sS -m 10 -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin123!"}' || echo FAIL

echo ""
echo "======== POST login via frontend proxy :3000 ========"
curl -sS -m 10 -X POST http://127.0.0.1:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin123!"}' || echo FAIL

echo ""
echo "======== GET ready via :3000 ========"
curl -sS -m 5 http://127.0.0.1:3000/api/v1/ready || echo FAIL

echo ""
echo "Expected login body includes access_token."
echo "Credentials: admin@example.com / Admin123!"
