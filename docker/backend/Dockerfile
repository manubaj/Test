FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for lxml / playwright optional runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install core runtime deps first (skip heavy ML packages in image by default
# for faster Windows docker pulls; agents use heuristic fallbacks).
RUN pip install --upgrade pip \
    && pip install \
        "fastapi>=0.115.0,<1.0" \
        "uvicorn[standard]>=0.32.0,<1.0" \
        "python-multipart>=0.0.12" \
        "pydantic>=2.9.0,<3.0" \
        "pydantic-settings>=2.6.0,<3.0" \
        "email-validator>=2.2.0" \
        "SQLAlchemy>=2.0.36,<3.0" \
        "asyncpg>=0.30.0" \
        "alembic>=1.14.0" \
        "greenlet>=3.1.0" \
        "python-jose[cryptography]>=3.3.0" \
        "passlib[bcrypt]>=1.7.4" \
        "bcrypt>=4.0.1,<4.1.0" \
        "httpx>=0.27.0" \
        "beautifulsoup4>=4.12.0" \
        "lxml>=5.3.0" \
        "langgraph>=0.2.0" \
        "langchain-core>=0.3.0" \
        "openpyxl>=3.1.5" \
        "pytest>=8.3.0" \
        "pytest-asyncio>=0.24.0"

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
