# Deployment Guide

## Docker Compose (single host / Windows Server / laptop)

```powershell
copy .env.example .env
# Set a strong SECRET_KEY and change admin password
docker compose up -d --build
```

Production hardening checklist:

1. Set `DEBUG=false` and a long random `SECRET_KEY`  
2. Change `BOOTSTRAP_ADMIN_PASSWORD` and rotate API key  
3. Restrict `CORS_ORIGINS` to your real frontend origin  
4. Put Compose behind a reverse proxy (IIS / nginx / Caddy) with TLS  
5. Back up the `postgres_data` volume  
6. Prefer Alembic migrations (`alembic upgrade head`) instead of create_all in locked-down environments  

## Scaling notes

- Rate limiter is in-memory — use Redis for multi-replica APIs  
- Ollama should run on a GPU host when using large models  
- Frontend is a static nginx image — CDN-friendly  

## Windows firewall

Allow inbound TCP ports you expose: `3000`, `8000` (and `5432`/`5050` only on trusted networks).

## Updating

```powershell
git pull
docker compose up -d --build
```
