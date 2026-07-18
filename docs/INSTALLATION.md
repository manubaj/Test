# Installation Guide (Windows)

## Option A — Docker Desktop (recommended)

1. Install Docker Desktop and ensure it is running (WSL2 backend recommended).
2. Clone this repository.
3. In PowerShell:

```powershell
cd path\to\Test
copy .env.example .env
docker compose up --build
```

4. Open http://localhost:3000 and login with `admin@example.com` / `Admin123!`.

### Stop / reset

```powershell
docker compose down
# Wipe database volume:
docker compose down -v
```

## Option B — Hybrid (Postgres/Ollama in Docker, app local)

Useful for active backend/frontend development.

```powershell
docker compose up -d postgres ollama pgadmin
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Edit .env DATABASE_URL host to localhost
uvicorn app.main:app --reload --port 8000

cd frontend
npm install
npm run dev
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 3000/8000/5432 in use | Stop conflicting apps or change ports in `docker-compose.yml` |
| Backend unhealthy | `docker compose logs backend` |
| Login fails after wipe | Recreate containers; admin is bootstrapped on startup |
| Crawl returns little text | Site may be JS-heavy; install Playwright browsers or rely on static HTML |
| Ollama slow on CPU | Skip model pull — heuristic agents still score leads |
