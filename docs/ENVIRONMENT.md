# Environment Variables

Copy `.env.example` to `.env` before running.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | AI Sales Intelligence Platform | App title |
| `APP_ENV` | development | Environment name |
| `DEBUG` | true | SQL echo / verbose logs |
| `API_PREFIX` | /api/v1 | REST prefix |
| `SECRET_KEY` | *(required in prod)* | JWT signing key (≥32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | JWT lifetime |
| `CORS_ORIGINS` | localhost:5173,3000 | Comma-separated origins |
| `DATABASE_URL` | postgresql+asyncpg://... | Async SQLAlchemy URL |
| `POSTGRES_*` | aisales / aisales_secret | Compose DB credentials |
| `LLM_PROVIDER` | ollama | `ollama` or `openai` |
| `OLLAMA_BASE_URL` | http://ollama:11434 | Ollama endpoint |
| `OLLAMA_MODEL` | llama3.2 | Local model name |
| `OPENAI_API_KEY` | empty | Used only when provider=openai |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model |
| `CRAWLER_MAX_PAGES` | 8 | Max pages per crawl |
| `RATE_LIMIT_REQUESTS` | 120 | Requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | 60 | Window size |
| `BOOTSTRAP_ADMIN_EMAIL` | admin@example.com | First admin |
| `BOOTSTRAP_ADMIN_PASSWORD` | Admin123! | First admin password |
| `BOOTSTRAP_ADMIN_API_KEY` | dev-api-key-change-me | Bootstrap API key |
| `VITE_API_BASE_URL` | http://localhost:8000/api/v1 | Frontend API base |
