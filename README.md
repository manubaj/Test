# AI Sales Intelligence Platform

Production-oriented platform that identifies companies likely to need ERP-related
services (IFS, SAP, Oracle, Infor, Microsoft Dynamics) using local/open-source
inference (Ollama, FAISS, Sentence Transformers, spaCy) with optional OpenAI
swap via configuration.

## Development approach

The project is built **module by module**. Each module must be approved before
the next begins.

| #  | Module              | Status                          |
|----|---------------------|---------------------------------|
| 1  | Folder structure    | Approved                        |
| 2  | Database models     | **In review**                   |
| 3  | Configuration       | Pending approval of Module 2    |
| 4  | FastAPI setup       | Pending                         |
| 5  | Crawling engine     | Pending                         |
| 6  | AI Agents           | Pending                         |
| 7  | LangGraph workflow  | Pending                         |
| 8  | REST APIs           | Pending                         |
| 9  | React frontend      | Pending                         |
| 10 | Docker              | Pending                         |
| 11 | Testing             | Pending                         |
| 12 | Deployment          | Pending                         |

## Module 1 — Folder structure

Clean-architecture layout under `app/` plus frontend, tests, Docker, and docs
placeholders. See [docs/MODULE_01_FOLDER_STRUCTURE.md](docs/MODULE_01_FOLDER_STRUCTURE.md).

```bash
python3 scripts/verify_structure.py
```

## Module 2 — Database models

SQLAlchemy 2.0 models for `companies`, `analysis`, `contacts`, `technologies`,
`lead_scores`, `crawl_logs`, `jobs`, `reports`, `users`, `settings`.
See [docs/MODULE_02_DATABASE_MODELS.md](docs/MODULE_02_DATABASE_MODELS.md).

```bash
pip3 install -r requirements.txt
python3 scripts/verify_models.py
```

## Stack (planned)

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic
- **AI:** LangGraph, Ollama (OpenAI-compatible via config), FAISS, Sentence Transformers, spaCy
- **Frontend:** React + TypeScript
- **Ops:** Docker Compose (PostgreSQL, pgAdmin, Ollama, backend, frontend)
