# Python-Stu — Enterprise FastAPI Backend

Enterprise-grade FastAPI + MongoDB backend with modular architecture.

## Tech Stack

- Python 3.12+, FastAPI, Pydantic v2
- MongoDB 7+, Motor, Beanie ODM
- Redis 7, JWT, bcrypt
- Docker, uv, Pytest, Loguru

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Docker (Recommended)

```bash
docker compose up -d
```

Visit http://localhost:8000/docs for Swagger UI.

### Local Development

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
| Method | Path                    | Description  |
|--------|-------------------------|--------------|
| POST   | /api/v1/auth/register   | Register     |
| POST   | /api/v1/auth/login      | Login        |
| POST   | /api/v1/auth/logout     | Logout       |
| POST   | /api/v1/auth/refresh    | Refresh token|

### Users
| Method | Path                  | Description          |
|--------|-----------------------|----------------------|
| GET    | /api/v1/users/me      | Current user profile |
| GET    | /api/v1/users         | User list (paginated)|
| POST   | /api/v1/users         | Create user (admin)  |
| GET    | /api/v1/users/{id}    | Get user by ID       |
| PUT    | /api/v1/users/{id}    | Update user          |
| DELETE | /api/v1/users/{id}    | Delete user (admin)  |

## Testing

```bash
cd backend
uv run pytest -v
```

## Project Structure

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

## Environment Variables

See `.env.example` for all configurable variables.

## Error Codes

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
