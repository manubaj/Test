# Architecture

## System context

```mermaid
flowchart LR
  User[Sales Analyst] --> UI[React Dashboard]
  UI --> API[FastAPI]
  API --> Auth[JWT / API Key / RBAC]
  API --> Svc[Analysis Service]
  Svc --> Graph[LangGraph Workflow]
  Graph --> Agents[7 AI Agents]
  Agents --> Crawl[Website Crawler]
  Agents --> LLM[Ollama or OpenAI]
  API --> DB[(PostgreSQL)]
  Svc --> DB
```

## Agent pipeline

```mermaid
flowchart TD
  A[Website Intelligence] --> B[Technology Detection]
  B --> C[ERP Opportunity Detection]
  C --> D[Hiring Intelligence]
  D --> E[Decision Maker Finder]
  E --> F[Lead Scoring]
  F --> G[Report Generator]
```

## Design principles

- **Clean architecture** — API → services/agents → repositories → models
- **Local-first AI** — Ollama default; heuristics keep the app usable offline
- **Provider swap** — `LLM_PROVIDER=ollama|openai` only
- **Async I/O** — FastAPI + SQLAlchemy async + httpx crawler
- **Repository pattern** — no SQL in routers
- **Config via `.env`** — no hardcoded secrets in code

## Data model (core)

- `companies` — prospect firmographics  
- `analysis` — one pipeline run + JSONB agent payloads  
- `technologies` / `contacts` / `lead_scores` / `reports` — structured outputs  
- `crawl_logs` / `jobs` — operational audit  
- `users` / `settings` — auth and configuration  

## Frontend surfaces

Company Search · Company Details · Website Analysis · Lead Score · Decision Makers · Technology Stack · ERP Detection · Hiring Analysis · News · Export CSV · Export Excel
