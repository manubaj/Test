# ERP Demand Discovery (primary product)

## What it does

You are an **ERP provider**. The platform discovers companies worldwide that
appear to need ERP solutions, then extracts public decision-maker contacts
for outreach.

**No manual ERP input** — a hardcoded catalog of major market ERPs is used
automatically (IFS, SAP, Oracle, Infor, Dynamics 365, NetSuite, Epicor, …).

## Flow

1. **Demand Discovery** — search LinkedIn-indexed jobs + public web  
2. **Website Enrichment** — crawl the company site  
3. **ERP Demand Confirmation** — map to hardcoded offerings  
4. **Hiring Signals** — ERP/cloud hiring score  
5. **Decision Maker & Contacts** — name, designation, location, email, phone (public only)  
6. **Lead Ranking** — top **100** leads

## Where to see it in the UI

1. Login → home page is **ERP demand discovery**  
2. Click **Start discovery (100 leads)**  
3. Review the lead table + click a row for contacts  
4. Export CSV / Excel  

## API

- `GET /api/v1/discovery/offerings` — hardcoded ERP catalog  
- `GET /api/v1/discovery/agents` — six agents  
- `POST /api/v1/discovery/runs` — `{ "target_lead_count": 100 }`  
- `GET /api/v1/discovery/runs/{id}/leads`  
- `GET /api/v1/discovery/runs/{id}/export/csv`  

## CLI

```bash
python -m app.agents --list-offerings
python -m app.agents --list-agents
python -m app.agents --discover --leads 100
```

## LinkedIn note

Direct authenticated LinkedIn scraping is not used (ToS / blocking). Discovery
uses **search-engine-indexed** LinkedIn job/company URLs, then enriches from
the company’s own website for contacts.
