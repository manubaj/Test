# Module 1 — Folder Structure

Status: **Complete — awaiting approval before Module 2 (Database Models)**

## Purpose

Establish the clean-architecture project skeleton for the AI Sales Intelligence Platform.
No business logic, database models, or API handlers are implemented in this module.

## Layout

```text
.
├── app/                          # Backend application (Python 3.12+)
│   ├── api/                      # FastAPI HTTP layer
│   │   ├── deps/                 # Dependency injection providers
│   │   └── v1/
│   │       └── endpoints/        # Versioned REST routers
│   ├── agents/                   # Independent AI agents + LangGraph
│   │   ├── website_intelligence/ # Agent 1
│   │   ├── erp_opportunity/      # Agent 2
│   │   ├── technology_detection/ # Agent 3
│   │   ├── hiring_intelligence/  # Agent 4
│   │   ├── decision_maker/       # Agent 5
│   │   ├── lead_scoring/         # Agent 6
│   │   ├── report_generator/     # Agent 7
│   │   └── workflow/             # LangGraph orchestration
│   ├── services/                 # Business services
│   │   ├── crawler/              # Playwright crawl engine
│   │   ├── analysis/             # Analysis orchestration
│   │   └── export/               # CSV / Excel export
│   ├── repositories/             # Repository pattern (data access)
│   ├── models/                   # SQLAlchemy ORM models
│   ├── database/                 # Engine, sessions, Base metadata
│   ├── schemas/                  # Pydantic schemas
│   ├── utils/                    # Shared helpers
│   └── core/                     # Settings, security, logging
├── alembic/                      # DB migrations
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── mocks/
├── frontend/                     # React + TypeScript dashboard
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       ├── types/
│       └── assets/
├── docker/                       # Service-specific Docker assets
│   ├── backend/
│   ├── frontend/
│   └── ollama/
├── data/
│   ├── faiss/                    # Local vector index storage
│   └── uploads/
├── docs/                         # Architecture & module docs
└── scripts/                      # Dev / ops helper scripts
```

## Architecture mapping

| Concern              | Package                         |
|----------------------|---------------------------------|
| Transport (HTTP)     | `app/api`                       |
| Use cases / domain   | `app/services`, `app/agents`    |
| Persistence          | `app/repositories`, `app/models`|
| Infrastructure       | `app/database`, `app/core`      |
| Contracts (DTO)      | `app/schemas`                   |
| Presentation (UI)    | `frontend/`                     |

## Verify this module

```bash
# From repository root
python3 scripts/verify_structure.py
```

Expected: exit code `0` and a printed checklist of required directories/packages.

## Import smoke test

```bash
python3 -c "import app; print(app.__app_name__, app.__version__)"
```

Expected output:

```text
AI Sales Intelligence Platform 0.1.0
```

## Next module (after approval)

**Module 2 — Database Models**

SQLAlchemy models for: `companies`, `analysis`, `contacts`, `technologies`,
`lead_scores`, `crawl_logs`, `jobs`, `reports`, `users`, `settings`.
