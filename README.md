# SignalForge — AI Sales Intelligence Platform

Identify companies likely to need **IFS**, **SAP**, **Oracle**, **Infor**, or **Microsoft Dynamics** services using a local-first AI stack (Ollama + heuristic agents). No paid OpenAI key is required.

## Quick start (Windows — recommended)

### Prerequisites

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) installed and running  
2. Git  
3. At least 8 GB RAM free (16 GB recommended if you pull an Ollama model)

### Run the full stack

```powershell
git clone <your-repo-url>
cd Test

# Create env file (PowerShell)
copy .env.example .env

# Start everything
docker compose up --build
```

When healthy:

| Service   | URL                                      |
|-----------|------------------------------------------|
| Frontend  | http://localhost:3000                    |
| API docs  | http://localhost:8000/docs               |
| Backend   | http://localhost:8000/api/v1/health      |
| pgAdmin   | http://localhost:5050 (`admin@example.com` / `admin`) |
| Ollama    | http://localhost:11434                   |

## Login troubleshooting

Use these credentials (exact email):

- Email: `admin@example.com`
- Password: `Admin123!`

Not `admin@aisales.local`.

```bash
# Rebuild after pulling login fixes
git pull origin main
docker compose up --build -d

# Diagnose
chmod +x scripts/diagnose-login.sh
./scripts/diagnose-login.sh
```

If curl login works but the UI does not, hard-refresh the browser (Ctrl+Shift+R).


### First analysis

1. Open http://localhost:3000 and sign in  
2. Add a company with a real website (e.g. a manufacturer’s public site)  
3. Click **Run full analysis**  
4. Review lead score, ERP detection, tech stack, hiring, decision makers, report  
5. Export CSV / Excel from the dashboard  

### Optional: pull a local LLM model

Agents work offline with rule-based detection. To enable Ollama summaries:

```powershell
docker exec -it aisales-ollama ollama pull llama3.2
```

### Switch to OpenAI later (config only)

Edit `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Restart backend: `docker compose up -d backend`

---

## Architecture

```text
React (SignalForge UI)
        │
        ▼
FastAPI REST (/api/v1) + JWT / API Key + RBAC + rate limits
        │
        ▼
AnalysisService → LangGraph workflow
        │
        ├─ Website Intelligence (crawl)
        ├─ Technology Detection
        ├─ ERP Opportunity Detection
        ├─ Hiring Intelligence
        ├─ Decision Maker Finder
        ├─ Lead Scoring
        └─ Report Generator
        │
        ▼
PostgreSQL (companies, analysis, contacts, technologies, …)
        │
Ollama (optional local LLM) / OpenAI (optional)
```

Clean architecture layout:

```text
app/
  api/          REST routers + auth dependencies
  agents/       7 AI agents + LangGraph workflow
  services/     crawler, analysis orchestration, export
  repositories/ data access
  models/       SQLAlchemy ORM
  schemas/      Pydantic contracts
  database/     engine/session/base
  core/         settings, security, logging
frontend/       React + TypeScript dashboard
docker/         Dockerfiles
```

---

## Local development (without Docker for app code)

### Backend (Windows PowerShell)

```powershell
# Python 3.12+
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings email-validator `
  SQLAlchemy asyncpg alembic greenlet "python-jose[cryptography]" "passlib[bcrypt]" `
  "bcrypt>=4.0.1,<4.1.0" httpx beautifulsoup4 lxml langgraph langchain-core openpyxl `
  pytest pytest-asyncio

# Point DB at local Postgres (or keep Docker only for Postgres)
copy .env.example .env
# Set DATABASE_URL=postgresql+asyncpg://aisales:aisales_secret@localhost:5432/aisales

docker compose up -d postgres ollama
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger: http://localhost:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173

### Tests

```powershell
pytest -q
```

### Structure / model checks

```powershell
python scripts/verify_structure.py
python scripts/verify_models.py
```

---

## REST API highlights

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/auth/login` | JWT login |
| GET | `/api/v1/companies` | Search (name, website, country, industry, technology, ERP, revenue, size) |
| POST | `/api/v1/companies` | Create company |
| POST | `/api/v1/analysis` | Run full multi-agent analysis |
| GET | `/api/v1/companies/{id}/intelligence` | Dashboard bundle |
| POST | `/api/v1/website/analyze` | Crawl preview |
| GET | `/api/v1/export/csv` | Export CSV |
| GET | `/api/v1/export/excel` | Export Excel |

Full interactive docs: `/docs` (Swagger) and `/redoc`.

---

## Security

- JWT Bearer authentication  
- Role-based access (`admin`, `analyst`, `viewer`)  
- API key support via `X-API-Key`  
- In-memory rate limiting  
- Pydantic input validation  
- Structured error responses  

---

## Documentation index

- [Installation Guide](docs/INSTALLATION.md)  
- [Architecture](docs/ARCHITECTURE.md)  
- [API Documentation](docs/API.md)  
- [Environment Variables](docs/ENVIRONMENT.md)  
- [Deployment Guide](docs/DEPLOYMENT.md)  
- Module notes: `docs/MODULE_01_*.md`, `docs/MODULE_02_*.md`

---

## Opportunity coverage

IFS Implementation / Upgrade / Cloud Migration / Managed Support · SAP S/4HANA Migration / Support · Infor Upgrade · Oracle ERP Migration · ERP Digital Transformation · ERP Performance Optimization
