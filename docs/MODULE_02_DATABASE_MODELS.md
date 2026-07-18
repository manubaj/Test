# Module 2 — Database Models

Status: **Complete — awaiting approval before Module 3 (Configuration)**

## Purpose

Define production-ready SQLAlchemy 2.0 ORM models for all core tables, with
UUID primary keys, timezone-aware timestamps, PostgreSQL JSONB payloads for
agent outputs, and explicit relationships.

## Tables

| Table          | Model        | Purpose                                      |
|----------------|--------------|----------------------------------------------|
| `users`        | `User`       | Auth, RBAC roles, optional API key hash      |
| `settings`     | `Setting`    | System / per-user JSON configuration         |
| `companies`    | `Company`    | Prospect firmographics + search fields       |
| `analysis`     | `Analysis`   | Multi-agent analysis run + JSON agent output |
| `contacts`     | `Contact`    | Decision makers (CEO/CIO/CTO/…)              |
| `technologies` | `Technology` | Detected ERP/cloud/DB/platform signals       |
| `lead_scores`  | `LeadScore`  | 0–100 score + factor explanation             |
| `crawl_logs`   | `CrawlLog`   | Website crawl audit trail                    |
| `jobs`         | `Job`        | Async crawl/analysis/export jobs             |
| `reports`      | `Report`     | Executive opportunity reports                |

## Key design choices

- **UUID PKs** — safer for distributed job APIs than sequential integers
- **JSONB** — flexible agent payloads without frequent migrations
- **Enums** — constrained statuses/roles (`app/models/enums.py`)
- **Cascade rules** — deleting a company removes dependent intelligence rows
- **Mixins** — `UUIDPrimaryKeyMixin` + `TimestampMixin` in `app/database/base.py`

## Entity relationships (simplified)

```text
User ─────────────┬──< Analysis
                  ├──< Job
                  └──< Setting

Company ──────────┬──< Analysis ──< LeadScore
                  ├──< Contact        └──< Report
                  ├──< Technology
                  ├──< CrawlLog
                  ├──< Job
                  └──< Report
```

## Files added

```text
app/database/base.py
app/database/__init__.py
app/models/enums.py
app/models/user.py
app/models/setting.py
app/models/company.py
app/models/analysis.py
app/models/contact.py
app/models/technology.py
app/models/lead_score.py
app/models/crawl_log.py
app/models/job.py
app/models/report.py
app/models/__init__.py
scripts/verify_models.py
requirements.txt
```

## Verify this module

```bash
pip3 install -r requirements.txt
python3 scripts/verify_models.py
```

Expected: exit code `0`, all 10 tables registered, FKs resolved, PostgreSQL DDL compiled.

## Notes

- No database engine, Alembic revision, or FastAPI wiring is included yet.
- Live PostgreSQL migrations arrive with Configuration / FastAPI modules.

## Next module (after approval)

**Module 3 — Configuration**

`.env` settings, Pydantic Settings, LLM provider switch (Ollama ↔ OpenAI),
logging, and security-related config constants.
