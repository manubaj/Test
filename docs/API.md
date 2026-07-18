# API Documentation

Interactive OpenAPI (Swagger): **http://localhost:8000/docs**  
ReDoc: **http://localhost:8000/redoc**

Base path: `/api/v1`

## Auth

### POST `/auth/login`

```json
{ "email": "admin@example.com", "password": "Admin123!" }
```

Response includes `access_token`. Send as:

```http
Authorization: Bearer <token>
```

Or use API key:

```http
X-API-Key: dev-api-key-change-me
```

## Companies

- `POST /companies` — create  
- `GET /companies` — search filters: `q`, `country`, `industry`, `technology`, `erp`, `revenue_min`, `revenue_max`, `employee_size`, `page`, `page_size`  
- `GET /companies/{id}` — details  
- `PATCH /companies/{id}` — update  
- `DELETE /companies/{id}` — soft archive (admin)

## Analysis

- `POST /analysis` body: `{ "company_id": "<uuid>" }` — runs all agents  
- `GET /analysis/{id}`  
- `GET /companies/{id}/intelligence` — dashboard aggregate  
- `GET /companies/{id}/contacts`  
- `GET /companies/{id}/technologies`  
- `GET /companies/{id}/lead-score`  
- `GET /companies/{id}/report`  
- `POST /website/analyze?url=https://example.com` — crawl preview  

## Export

- `GET /export/csv`  
- `GET /export/excel`  

## Health

- `GET /health`  
- `GET /ready`  

## Status codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Conflict |
| 422 | Validation error |
| 429 | Rate limited |
