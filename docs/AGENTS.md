# Six AI Agents — ERP Sales Intelligence Tool

The platform exposes **one tool** that runs **six analysis agents** (plus a
report synthesizer), matching the original product brief.

## Agents

| # | Agent | Output |
|---|-------|--------|
| 1 | Website Intelligence | Crawl, products, ERP/cloud/DB/languages, industry (JSON) |
| 2 | ERP Opportunity Detection | Upgrade/migration/expansion signals + confidence |
| 3 | Technology Detection | IFS/SAP/Infor/Oracle/Dynamics/Salesforce/Azure/AWS/GCP/SQL/Oracle DB/PostgreSQL/K8s/Docker |
| 4 | Hiring Intelligence | Careers analysis + hiring score |
| 5 | Decision Maker Finder | CEO/CIO/CTO/VP IT/IT Director/ERP Manager/… + profile links |
| 6 | Lead Scoring | 0–100 with ERP=30, Manufacturing=10, Hiring=20, Cloud=20, Expansion=20 |
| — | Report Generator | Executive summary, opportunity, services, deal size, priority, next action |

## Run the tool (CLI)

```bash
# List agents
python -m app.agents --list-agents

# Run all six against a website
python -m app.agents --name "Acme Manufacturing" --website https://example.com
```

## Run via API

```http
GET  /api/v1/agents
POST /api/v1/agents/run
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_name": "Acme Manufacturing",
  "website": "https://example.com"
}
```

Response includes `agents.agent_1_…` through `agents.agent_6_…`, `agent_trace`,
and `report`.

## Run via UI

Company page → **Run full analysis** → **Six AI agents** panel shows each
agent’s status, timing, and JSON outputs.
