# AGENTS.md — Project Guidelines

## Project Overview
Enterprise-grade FastAPI + MongoDB backend with modular architecture.

## Tech Stack
- Python 3.12+, FastAPI, Pydantic v2, Uvicorn
- MongoDB 7+, Motor, Beanie ODM
- Redis, JWT, bcrypt
- uv (dependency management)
- Docker, Pytest, Loguru

## Architecture Rules

### Strict Layering (MANDATORY)
```
Router → Service → Repository → ODM (Beanie)
```
- **Router**: parameter validation + return only
- **Service**: business logic only
- **Repository**: MongoDB CRUD only
- **Never** put database code in router or service

### Code Conventions
- All I/O must be `async/await`
- Type hints required on all function signatures
- Docstrings: Google style
- No print statements — use `loguru`
- Imports order: stdlib → third-party → local (separated by blank line)

### Data Model Conventions (MANDATORY)
- **ID type**: All document `_id` fields use `str`, generated via `lambda: str(uuid4())`
  ```python
  id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
  ```
- **Foreign keys**: All reference IDs use `str` (e.g. `company_id: str`, `user_id: str`)
- **Timestamps**: All time fields use `int` (millisecond Unix timestamp), generated via `int(time.time() * 1000)`
  ```python
  created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
  updated_at: int = Field(default_factory=lambda: int(time.time() * 1000))
  ```
- **Update timestamps**: Repositories MUST set `update_data["updated_at"] = int(time.time() * 1000)` on every update
- **DO NOT** import or use `UUID` type or `datetime` type in models or schemas

### Response Format (ALL endpoints)
```json
{"code": 0, "message": "success", "data": {}}
```
Error responses use business error codes (10001+).

### API Convention
- Prefix: `/api/v1/`
- Version in URL path
- Dependency injection via `Depends()` for auth

### Token & Auth
- JWT access_token (short-lived, configurable TTL)
- JWT refresh_token (longer TTL, stored in Redis)
- Token revocation via Redis blacklist on logout
- `get_current_user()` as FastAPI dependency

### Testing
- pytest + httpx AsyncClient
- Tests mirror `app/` structure under `tests/`
- Each test file: `test_<module>.py`
- Mock external services (MongoDB, Redis) where possible

### Project Lifecycle
1. Design → docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
2. Implementation plan → execute via writing-plans skill
3. No code changes without approved design

## File Structure
```
backend/
├── app/
│   ├── main.py
│   ├── core/           → config, security, logger, exceptions
│   ├── api/v1/         → router, deps, endpoints
│   ├── models/         → Beanie Documents
│   ├── schemas/        → Pydantic schemas
│   ├── services/       → business logic
│   ├── repositories/   → MongoDB CRUD
│   ├── database/       → mongodb.py, redis.py
│   ├── utils/          → response.py, pagination.py
│   ├── middleware/     → auth middleware
│   └── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```
