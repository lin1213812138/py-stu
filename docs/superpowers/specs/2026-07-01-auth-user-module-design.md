# Auth & User Module — Design Spec

**Date:** 2026-07-01
**Project:** python-stu — Enterprise FastAPI + MongoDB Backend

---

## 1. Overview

Build the foundation of an enterprise-grade FastAPI backend: authentication system (register, login, logout, JWT, refresh token) and user management (CRUD, pagination, role base). The project structure is designed from day one to support future modules (RBAC, menu management, API permissions, audit logging).

## 2. Architecture

### Layering (MANDATORY)

```
Router → Service → Repository → ODM (Beanie)

Router:       parameter validation + response formatting only
Service:      business logic, orchestration, error handling
Repository:   MongoDB CRUD operations only
ODM (Beanie): Document models, indexes, DB operations
```

### Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app, middleware, router mount
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # pydantic-settings → .env
│   │   ├── security.py         # JWT encode/decode, bcrypt hash/verify
│   │   ├── logger.py           # Loguru config
│   │   └── exceptions.py       # AppException hierarchy + global handler
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # get_current_user(), require_role()
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # aggregate all v1 routers
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py     # register, login, logout, refresh
│   │           └── user.py     # /me, list, create, get, update, delete
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # Beanie Document
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # RegisterRequest, LoginRequest, TokenResponse
│   │   └── user.py             # UserCreate, UserUpdate, UserResponse
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # register, login, logout, refresh_token
│   │   └── user_service.py     # CRUD orchestration, duplicate check
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py  # create, get_by_id, get_by_username, get_list, update, delete
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mongodb.py          # init_beanie(), connect/disconnect
│   │   └── redis.py            # Redis pool: get, set, delete
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── response.py         # APIResponse base model
│   │   └── pagination.py       # PageParams, PageResult
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # request logging middleware
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py         # pytest fixtures, test app, test DB
│       ├── test_auth.py
│       └── test_user.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## 3. Technology Stack

| Component        | Choice                | Reason                          |
|------------------|-----------------------|---------------------------------|
| Runtime          | Python 3.12+          | Latest stable                   |
| Web framework    | FastAPI               | Async-first, auto-docs          |
| Server           | Uvicorn               | ASGI, production-ready          |
| Validation       | Pydantic v2           | FastAPI native, fast            |
| ODM              | Beanie                | Async, Motor-based              |
| Database         | MongoDB 7+            | Document DB                     |
| Cache / Token    | Redis 7               | Token blacklist, refresh tokens |
| Auth             | PyJWT + bcrypt        | Industry standard               |
| Logging          | Loguru                | Structured, zero-config         |
| Dependency mgmt  | uv                    | Fast, modern                    |
| Testing          | pytest + httpx        | Async test support              |
| Containerization | Docker + compose      | Reproducible env                |

## 4. Data Model

### User Document (Beanie)

```python
class User(Document):
    id: UUID = Field(default_factory=uuid4)       # Primary key, UUID
    username: str                                  # unique index
    email: str                                     # unique index
    password_hash: str
    nickname: str | None = None
    avatar: str | None = None
    role: str = "user"                             # user | admin (future RBAC base)
    status: int = 1                                # 1=active, 0=disabled
    last_login_time: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel("username", unique=True),
            IndexModel("email", unique=True),
        ]
```

**ID type:** UUID (v4) — all API route paths using `{user_id}` accept UUID format.

## 5. Authentication Design

### Token Strategy

| Token         | Storage            | TTL (default) |
|---------------|--------------------|---------------|
| access_token  | Client-side        | 30 min        |
| refresh_token | Redis (keyed)      | 7 days        |

- **access_token** payload: `{ sub: user_id, username, role, exp, iat }`
- **refresh_token** payload: `{ sub: user_id, type: "refresh", exp }`
- Token blacklist on logout: access_token hash stored in Redis for remaining TTL

### Endpoints

| Method | Path                    | Auth    | Description             |
|--------|-------------------------|---------|-------------------------|
| POST   | `/api/v1/auth/register` | None    | Create new user         |
| POST   | `/api/v1/auth/login`    | None    | Authenticate, get tokens |
| POST   | `/api/v1/auth/logout`   | Bearer  | Revoke tokens           |
| POST   | `/api/v1/auth/refresh`  | Bearer  | Rotate refresh token    |

### Register Flow
1. Validate request (username, email, password)
2. Check username uniqueness → 10002 if exists
3. Check email uniqueness → 10002 if exists
4. Hash password with bcrypt
5. Repository.create()
6. Return UserResponse (no password_hash)

### Login Flow
1. Find user by username → 10004 if not found
2. Verify password with bcrypt → 10004 if mismatch
3. Check user status → 10001 if disabled
4. Generate access_token + refresh_token
5. Store refresh_token in Redis
6. Update last_login_time
7. Return TokenResponse

### Logout Flow
1. Extract user_id from access_token
2. Delete refresh_token from Redis
3. Add access_token jti to Redis blacklist
4. Return success

## 6. User Management

### Endpoints

| Method | Path                      | Auth    | Role   | Description          |
|--------|---------------------------|---------|--------|----------------------|
| GET    | `/api/v1/users/me`        | Bearer  | *      | Current user profile |
| GET    | `/api/v1/users`           | Bearer  | *      | User list (paginated)|
| POST   | `/api/v1/users`           | Bearer  | admin  | Create user          |
| GET    | `/api/v1/users/{user_id}` | Bearer  | *      | Get user by ID       |
| PUT    | `/api/v1/users/{user_id}` | Bearer  | *      | Update user          |
| DELETE | `/api/v1/users/{user_id}` | Bearer  | admin  | Delete user          |

### Pagination

```python
class PageParams:
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1, le=100)
    username: str | None = None     # filter
    email: str | None = None        # filter
    status: int | None = None       # filter

class PageResult:
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

### Self vs Admin Rules
- GET /users/me — only self data
- GET /users — all users (authenticated)
- GET /users/{id} — any authenticated user
- PUT /users/{id} — self or admin
- DELETE /users/{id} — admin only
- POST /users — admin only

## 7. Response Format

### Success
```json
{"code": 0, "message": "success", "data": {}}
```

### Error
```json
{"code": 10001, "message": "description", "data": null}
```

### Error Codes

| Code  | Description              |
|-------|--------------------------|
| 0     | Success                  |
| 10001 | General business error   |
| 10002 | User already exists      |
| 10003 | User not found           |
| 10004 | Invalid credentials      |
| 10005 | Token expired/invalid    |
| 10006 | Insufficient permissions |
| 10007 | Validation error         |

## 8. Dependency Injection

```python
# api/deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis)
) -> User:
    """Decode JWT, check blacklist, return User."""

def require_role(role: str):
    """Return Depends() that checks user.role >= required role."""
```

## 9. Configuration (.env)

```ini
APP_NAME=python-stu
ENV=development

MONGODB_URL=mongodb://mongo:27017
MONGODB_DATABASE=app

REDIS_URL=redis://redis:6379

JWT_SECRET=change-this-in-production
JWT_ACCESS_EXPIRE=1800       # 30 min
JWT_REFRESH_EXPIRE=604800    # 7 days
```

## 10. Docker

### docker-compose.yml

```yaml
services:
  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
    volumes: [mongo_data:/data/db]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [mongodb, redis]

volumes:
  mongo_data:
```

## 11. Quality

### Global Error Handler
- Catches all `AppException` → formatted error response
- Catches unexpected exceptions → 500, logged with traceback

### CORS
- Configurable origins via `CORS_ORIGINS` env
- Default: `["*"]` for development

### Request Logging
- Middleware logs: `[YYYY-MM-DD HH:mm:ss] METHOD /path -> status (duration)`

### API Versioning
- URL path prefix: `/api/v1/`
- Versioned router aggregation in `api/v1/router.py`

### Testing
- Repository tests: mock Beanie
- Service tests: mock Repository
- API tests: httpx AsyncClient with test app
- Fixtures: test MongoDB (mongomock), test Redis (fakeredis)

## 12. Future Extensibility

The architecture explicitly supports adding:

| Module        | Extension Point              |
|---------------|------------------------------|
| RBAC          | Extend `role` → `permissions` array + Permission model |
| Menu/API mgmt | New Document models + CRUD endpoints |
| Audit log     | Middleware intercepts write operations |
| Rate limit    | Middleware checks Redis counter |
| Notification  | Event bus after auth actions |

## 13. Out of Scope (Phase 1)

- Email verification / password reset flows
- OAuth / social login
- Rate limiting
- Soft delete
- Advanced RBAC (role-permission matrix)
- Audit logging
- File upload (avatar)
