# Environment Config & Packaging — Design Spec

**Date:** 2026-07-01
**Project:** python-stu — Enterprise FastAPI + MongoDB Backend

---

## 1. Overview

Re-engineer the environment variable configuration system to support four environments (dev, test, staging, production) and revamp the packaging strategy for multi-environment deployment. The design follows 12-Factor App principles: **one build artifact, runtime configuration**.

### Goals
- Dynamic `.env.{env}` file loading based on `ENV` system variable
- Python wheel packaging via hatchling
- Multi-stage Docker build for production
- Clear separation between build-time code and runtime config

### Non-Goals
- No build-time env embedding (secrets never baked into images)
- No environment-specific Dockerfiles (single Dockerfile for all envs)

---

## 2. Architecture: Config Loading

### Flow

```
System env sets: ENV=production
         │
         ▼
Settings.__init__() → os.getenv("ENV", "development")
         │
         ▼
pydantic-settings loads .env.{ENV} (e.g. .env.production)
         │
         ▼
settings singleton with env-specific values
```

### Key Rules
- `ENV` must be set via **system environment variable** (not in env file — chicken-and-egg)
- Fallback chain: `.env.{ENV}` → `.env` → pydantic-settings defaults
- System environment variables always override file values (pydantic-settings native behavior)

---

## 3. File Structure

```
backend/
├── .env                    # Legacy fallback (same as .env.development)
├── .env.example            # Template with placeholder values
├── .env.development        # Local development (localhost)
├── .env.test               # CI / automated testing
├── .env.staging            # Pre-production environment
├── .env.production         # Production environment
├── app/core/config.py      # Modified: dynamic env_file loading
├── Dockerfile              # Rewritten: multi-stage build
├── docker-compose.yml      # Modified: env_file switch by ENV
├── .dockerignore           # NEW: exclude dev artifacts
└── pyproject.toml          # Unchanged (hatchling already configured)
```

### Environment File Differences

| Variable | `.env.development` | `.env.test` | `.env.staging` | `.env.production` |
|---|---|---|---|---|
| `MONGODB_URL` | `localhost` | `localhost` | `staging-mongo:27017` | `prod-mongo:27017` |
| `REDIS_URL` | `localhost` | `localhost` | `staging-redis:6379` | `prod-redis:6379` |
| `JWT_SECRET` | `dev-secret` | `test-secret` | `staging-secret` | `prod-secret` |
| `JWT_ACCESS_EXPIRE` | `1800` | `1800` | `1800` | `1800` |
| `JWT_REFRESH_EXPIRE` | `604800` | `604800` | `604800` | `604800` |
| `CORS_ORIGINS` | `["*"]` | `["*"]` | `["https://staging.example.com"]` | `["https://example.com"]` |

---

## 4. Config Module Changes

**File:** `backend/app/core/config.py`

### Current (before):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    ...
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### After:
```python
import os
from pathlib import Path
from pydantic_settings import BaseSettings

_env = os.getenv("ENV", "development")

class Settings(BaseSettings):
    ENV: str = _env
    APP_NAME: str = "python-stu"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "app"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change-this-in-production"
    JWT_ACCESS_EXPIRE: int = 1800
    JWT_REFRESH_EXPIRE: int = 604800
    CORS_ORIGINS: list[str] = ["*"]

    @classmethod
    def _env_file(cls) -> str:
        env_specific = f".env.{cls._env}"
        if Path(env_specific).exists():
            return [env_specific, ".env"]
        return ".env"

    model_config = {
        "env_file_encoding": "utf-8",
    }

settings = Settings()
```

- `ENV` read from system env, default `"development"`
- Primary env file: `.env.{ENV}`, fallback to `.env`
- All secrets/config stay in files, never in image layers

---

## 5. Packaging Strategy

### 5.1 Python Wheel

```bash
hatch build    # produces dist/python_stu-0.1.0-py3-none-any.whl
```

- Single wheel for all environments
- Wheel contains `app/` package only — **no `.env.*` files**
- Deployment: `pip install wheel` + mount/create `.env.{env}` at runtime

### 5.2 Docker Multi-Stage Build

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev --frozen
COPY . .
RUN uv build --wheel --out-dir /dist

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /dist/*.whl /tmp/
RUN pip install /tmp/*.whl --no-cache-dir && \
    rm -f /tmp/*.whl && \
    groupadd -r appuser && useradd -r -g appuser -u 1000 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Key differences from current:
- **Multi-stage:** builder + runtime, slim final image
- **No `--reload` in CMD:** only for dev
- **Non-root user:** run as `appuser` (uid 1000)
- **uv build → wheel:** proper isolated build
- **No dev dependencies** in final image

### 5.3 Docker Compose Update

```yaml
services:
  backend:
    build: .
    ports: ["8000:8000"]
    env_file:
      - .env.${ENV:-development}
    environment:
      - ENV=${ENV:-development}
    ...
```

---

## 6. Env File Loading Edge Cases

| Scenario | Behavior |
|---|---|
| `ENV` not set, `.env.development` missing | Fallback to `.env`, then pydantic-settings defaults |
| `ENV=production`, `.env.production` missing | Use system env vars + defaults only (K8s pattern) |
| System env var + env file both set same key | System env wins (pydantic-settings native behavior) |
| `ENV` contains unexpected value (e.g. `dev2`) | Load `.env.dev2` if exists, else fallback `.env` |
| Wheel installed, no `.env.*` files present | All settings fall through to class defaults |

---

## 7. Files to Create / Modify

| File | Action | Purpose |
|---|---|---|
| `.env.development` | Create | Dev env config (copy from existing `.env`) |
| `.env.test` | Create | CI/test env config |
| `.env.staging` | Create | Staging env config |
| `.env.production` | Create | Production env config |
| `.dockerignore` | Create | Exclude `.venv`, `__pycache__`, `logs`, `.git` |
| `app/core/config.py` | Modify | Dynamic env_file loading + fallback |
| `Dockerfile` | Rewrite | Multi-stage build |
| `docker-compose.yml` | Modify | Dynamic env_file via `ENV` |

No changes needed to:
- `pyproject.toml` (hatchling already configured)
- `.gitignore` (`.env` already ignored; `.env.*.example` could be tracked)
- Any router / service / repository code (settings consumption unchanged)

---

## 8. Future Considerations

- **Secret management service** (Vault / AWS Parameter Store): can be added later as a `Settings` custom source without changing consumer code
- **`.env.example` per environment**: optional `.env.development.example`, `.env.production.example` if needed for onboarding
- **CI integration**: test env can inject `ENV=test` and mount `.env.test` via CI secrets
