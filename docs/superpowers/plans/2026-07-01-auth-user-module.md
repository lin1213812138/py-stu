# Auth & User Module — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build enterprise-grade FastAPI + MongoDB authentication system and user management module.

**Architecture:** Strict 4-layer routing (Router → Service → Repository → ODM) with JWT auth, Redis-backed token blacklist, UUID primary keys, and unified JSON response format.

**Tech Stack:** Python 3.12+, FastAPI, Beanie ODM, MongoDB 7, Redis 7, PyJWT, bcrypt, Loguru, uv, Docker, Pytest + httpx.

## Global Constraints

- All I/O must be `async/await`
- Type hints required on all function signatures
- Docstrings: Google style
- No `print` — use `from loguru import logger`
- Imports order: stdlib → third-party → local (separated by blank line)
- Response format: `{"code": 0, "message": "success", "data": {}}`
- Error codes: 0=success, 10001=general, 10002=user exists, 10003=not found, 10004=invalid credentials, 10005=token invalid, 10006=no permission, 10007=validation
- API prefix: `/api/v1/`
- UUID v4 for all user IDs (both in DB and API paths)
- Dependency injection via `Depends()` for auth

---

### Task 1: Project Scaffold

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/Dockerfile`
- Create: `backend/docker-compose.yml`
- Create: `backend/.gitignore`
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/endpoints/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/repositories/__init__.py`
- Create: `backend/app/database/__init__.py`
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/middleware/__init__.py`
- Create: `backend/app/tests/__init__.py`

**Interfaces:**
- Produces: directory structure + dependency manifest

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "python-stu"
version = "0.1.0"
description = "Enterprise FastAPI + MongoDB backend"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.0,<3",
    "pydantic-settings>=2.0",
    "motor>=3.6.0",
    "beanie>=1.28.0",
    "redis[hiredis]>=5.2.0",
    "pyjwt>=2.9.0",
    "bcrypt>=4.2.0",
    "loguru>=0.7.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["app/tests"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Create .env.example**

```ini
APP_NAME=python-stu
ENV=development

MONGODB_URL=mongodb://mongo:27017
MONGODB_DATABASE=app

REDIS_URL=redis://redis:6379

JWT_SECRET=change-this-in-production
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["*"]
```

- [ ] **Step 3: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 4: Create docker-compose.yml**

```yaml
services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - mongodb
      - redis
    restart: unless-stopped

volumes:
  mongo_data:
```

- [ ] **Step 5: Create .gitignore**

```
__pycache__/
*.pyc
.env
.venv/
.idea/
*.egg-info/
dist/
```

- [ ] **Step 6: Create all `__init__.py` files (empty)**

Create empty `__init__.py` in each package directory listed above.

- [ ] **Step 7: Verify scaffold**

```bash
cd backend
uv sync
uv run python -c "import fastapi; print(fastapi.__version__)"
```
Expected: prints FastAPI version with no errors.

---

### Task 2: Core Infrastructure (Config, Security, Logger, Exceptions, Utils)

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/logger.py`
- Create: `backend/app/core/exceptions.py`
- Create: `backend/app/utils/response.py`
- Create: `backend/app/utils/pagination.py`

**Interfaces:**
- Produces: `settings` (config singleton), `hash_password()`, `verify_password()`, `create_access_token()`, `create_refresh_token()`, `decode_token()`, `AppException` hierarchy, `APIResponse`, `PageParams`, `PageResult`

- [ ] **Step 1: Write core/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "python-stu"
    ENV: str = "development"

    MONGODB_URL: str = "mongodb://mongo:27017"
    MONGODB_DATABASE: str = "app"

    REDIS_URL: str = "redis://redis:6379"

    JWT_SECRET: str = "change-this-in-production"
    JWT_ACCESS_EXPIRE: int = 1800
    JWT_REFRESH_EXPIRE: int = 604800

    CORS_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 2: Write core/security.py**

```python
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: UUID, username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_ACCESS_EXPIRE)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_REFRESH_EXPIRE)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
```

- [ ] **Step 3: Write core/logger.py**

```python
import sys

from loguru import logger


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {name}:{function}:{line} | {message}",
        level="INFO",
        colorize=True,
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
    )


setup_logger()
```

- [ ] **Step 4: Write core/exceptions.py**

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    def __init__(self, code: int = 10001, message: str = "Business error"):
        self.code = code
        self.message = message


class UserExistsError(AppException):
    def __init__(self):
        super().__init__(code=10002, message="User already exists")


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__(code=10003, message="User not found")


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(code=10004, message="Invalid username or password")


class TokenError(AppException):
    def __init__(self):
        super().__init__(code=10005, message="Token expired or invalid")


class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(code=10006, message="Insufficient permissions")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=400,
            content={"code": exc.code, "message": exc.message, "data": None},
        )
    logger.opt(exception=True).error(f"Unhandled: {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 10001, "message": "Internal server error", "data": None},
    )
```

- [ ] **Step 5: Write utils/response.py**

```python
from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
```

- [ ] **Step 6: Write utils/pagination.py**

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

- [ ] **Step 7: Test core/security.py**

Create `backend/tests/test_security.py`:

```python
import pytest
from app.core.security import hash_password, verify_password, decode_token, create_access_token, create_refresh_token
from uuid import uuid4


def test_password_hash_and_verify():
    hashed = hash_password("test123")
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token():
    uid = uuid4()
    token = create_access_token(uid, "alice", "user")
    payload = decode_token(token)
    assert payload["sub"] == str(uid)
    assert payload["username"] == "alice"
    assert payload["role"] == "user"
    assert payload["type"] == "access"


def test_refresh_token():
    uid = uuid4()
    token = create_refresh_token(uid)
    payload = decode_token(token)
    assert payload["sub"] == str(uid)
    assert payload["type"] == "refresh"
```

- [ ] **Step 8: Run tests**

```bash
cd backend
uv run pytest tests/test_security.py -v
```
Expected: 3 passed.

---

### Task 3: Database Layer (MongoDB + Redis)

**Files:**
- Create: `backend/app/database/mongodb.py`
- Create: `backend/app/database/redis.py`

**Interfaces:**
- Produces: `init_db()`, `get_redis()` (FastAPI dependency returning Redis client)

- [ ] **Step 1: Write database/mongodb.py**

```python
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from app.core.config import settings


async def init_db() -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    await init_beanie(
        database=db,
        document_models=[
            "app.models.user.User",
        ],
    )
    logger.info(f"MongoDB connected: {settings.MONGODB_URL}/{settings.MONGODB_DATABASE}")
```

- [ ] **Step 2: Write database/redis.py**

```python
from redis.asyncio import Redis
from loguru import logger

from app.core.config import settings

redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_client
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.ping()
    logger.info(f"Redis connected: {settings.REDIS_URL}")


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> Redis:
    return redis_client
```

---

### Task 4: User Model + Repository

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/repositories/user_repository.py`

**Interfaces:**
- Produces: `User` Beanie Document, `UserRepository` class with `create`, `get_by_id`, `get_by_username`, `get_by_email`, `get_list`, `update`, `delete`, `count`

- [ ] **Step 1: Write models/user.py**

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    username: str = Indexed(unique=True)
    email: str = Indexed(unique=True)
    password_hash: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"
    status: int = 1
    last_login_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "alice",
                "email": "alice@example.com",
            }
        },
        "populate_by_name": True,
    }
```

- [ ] **Step 2: Write repositories/user_repository.py**

```python
from typing import Optional
from uuid import UUID

from app.models.user import User
from app.utils.pagination import PageParams, PageResult


class UserRepository:

    @staticmethod
    async def create(user: User) -> User:
        return await user.insert()

    @staticmethod
    async def get_by_id(user_id: UUID) -> Optional[User]:
        return await User.get(user_id)

    @staticmethod
    async def get_by_username(username: str) -> Optional[User]:
        return await User.find_one(User.username == username)

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    @staticmethod
    async def get_list(params: PageParams, username: Optional[str] = None, email: Optional[str] = None, status: Optional[int] = None) -> PageResult[User]:
        query = {}
        if username:
            query["username"] = {"$regex": username, "$options": "i"}
        if email:
            query["email"] = {"$regex": email, "$options": "i"}
        if status is not None:
            query["status"] = status

        total = await User.find(query).count()
        items = await User.find(query).skip((params.page - 1) * params.page_size).limit(params.page_size).to_list()

        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
        )

    @staticmethod
    async def update(user_id: UUID, update_data: dict) -> Optional[User]:
        user = await User.get(user_id)
        if not user:
            return None
        update_data["updated_at"] = datetime.utcnow()
        await user.update({"$set": update_data})
        return await User.get(user_id)

    @staticmethod
    async def delete(user_id: UUID) -> bool:
        user = await User.get(user_id)
        if not user:
            return False
        await user.delete()
        return True

    @staticmethod
    async def count(filters: Optional[dict] = None) -> int:
        return await User.find(filters or {}).count()
```

Note: `datetime` import needed. Add to imports:

```python
from datetime import datetime
```

---

### Task 5: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/user.py`

**Interfaces:**
- Produces: `RegisterRequest`, `LoginRequest`, `TokenResponse`, `RefreshRequest`, `UserCreate`, `UserUpdate`, `UserResponse`

- [ ] **Step 1: Write schemas/auth.py**

```python
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
```

- [ ] **Step 2: Write schemas/user.py**

```python
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    status: Optional[int] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    status: int
    last_login_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

### Task 6: API Dependencies

**Files:**
- Create: `backend/app/api/deps.py`

**Interfaces:**
- Produces: `get_current_user() -> User` (FastAPI dependency), `require_role(role: str)` (dependency factory), `get_redis()` reusable

- [ ] **Step 1: Write api/deps.py**

```python
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.core.exceptions import TokenError, PermissionDeniedError
from app.core.security import decode_token
from app.database.redis import get_redis
from app.models.user import User
from app.repositories.user_repository import UserRepository

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise TokenError()

    blacklisted = await redis.get(f"blacklist:{token}")
    if blacklisted:
        raise TokenError()

    user = await UserRepository.get_by_id(UUID(payload["sub"]))
    if not user or user.status == 0:
        raise TokenError()

    return user


def require_role(required_role: str):
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise PermissionDeniedError()
        return current_user
    return role_checker
```

---

### Task 7: Services

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/services/user_service.py`

**Interfaces:**
- Produces: `AuthService.register()`, `AuthService.login()`, `AuthService.logout()`, `AuthService.refresh_token()`, `UserService.create_user()`, `UserService.get_user()`, `UserService.get_user_list()`, `UserService.update_user()`, `UserService.delete_user()`

- [ ] **Step 1: Write services/auth_service.py**

```python
from datetime import datetime
from uuid import UUID

from redis.asyncio import Redis

from app.core.exceptions import InvalidCredentialsError, TokenError, UserExistsError
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.database.redis import get_redis
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse


class AuthService:

    def __init__(self):
        self.repo = UserRepository()

    async def register(self, username: str, email: str, password: str) -> User:
        existing = await self.repo.get_by_username(username)
        if existing:
            raise UserExistsError()
        existing = await self.repo.get_by_email(email)
        if existing:
            raise UserExistsError()

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        return await self.repo.create(user)

    async def login(self, username: str, password: str, redis: Redis) -> TokenResponse:
        user = await self.repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        if user.status == 0:
            raise InvalidCredentialsError()

        access_token = create_access_token(user.id, user.username, user.role)
        refresh_token = create_refresh_token(user.id)

        await redis.set(f"refresh_token:{user.id}", refresh_token)

        user.last_login_time = datetime.utcnow()
        await user.save()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, user_id: UUID, access_token: str, redis: Redis) -> None:
        await redis.delete(f"refresh_token:{user_id}")
        from app.core.config import settings
        await redis.setex(f"blacklist:{access_token}", settings.JWT_ACCESS_EXPIRE, "1")

    async def refresh_token(self, refresh_token: str, redis: Redis) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise TokenError()

        if payload.get("type") != "refresh":
            raise TokenError()

        user_id = UUID(payload["sub"])
        stored = await redis.get(f"refresh_token:{user_id}")
        if stored != refresh_token:
            raise TokenError()

        user = await self.repo.get_by_id(user_id)
        if not user or user.status == 0:
            raise TokenError()

        new_access = create_access_token(user.id, user.username, user.role)
        new_refresh = create_refresh_token(user.id)
        await redis.set(f"refresh_token:{user.id}", new_refresh)

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
```

- [ ] **Step 2: Write services/user_service.py**

```python
from typing import Optional
from uuid import UUID

from app.core.exceptions import UserNotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.utils.pagination import PageParams, PageResult


class UserService:

    def __init__(self):
        self.repo = UserRepository()

    async def get_me(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_list(
        self,
        params: PageParams,
        username: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult[User]:
        return await self.repo.get_list(params, username, email, status)

    async def get_user(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def create_user(self, data: UserCreate) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            nickname=data.nickname,
            avatar=data.avatar,
            role=data.role,
        )
        return await self.repo.create(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        update_dict = data.model_dump(exclude_unset=True)
        user = await self.repo.update(user_id, update_dict)
        if not user:
            raise UserNotFoundError()
        return user

    async def delete_user(self, user_id: UUID) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise UserNotFoundError()
```

---

### Task 8: API Endpoints + Main App + Middleware

**Files:**
- Create: `backend/app/api/v1/endpoints/auth.py`
- Create: `backend/app/api/v1/endpoints/user.py`
- Create: `backend/app/api/v1/router.py`
- Create: `backend/app/middleware/auth.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Write endpoints/auth.py**

```python
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis

from app.api.deps import get_current_user, security_scheme
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.utils.response import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


@router.post("/register")
async def register(body: RegisterRequest) -> APIResponse:
    user = await service.register(body.username, body.email, body.password)
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("/login")
async def login(body: LoginRequest, redis: Annotated[Redis, Depends(get_redis)]) -> APIResponse:
    tokens = await service.login(body.username, body.password, redis)
    return APIResponse(data=tokens.model_dump())


@router.post("/logout")
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> APIResponse:
    await service.logout(current_user.id, credentials.credentials, redis)
    return APIResponse(message="logout success")


@router.post("/refresh")
async def refresh(body: RefreshRequest, redis: Annotated[Redis, Depends(get_redis)]) -> APIResponse:
    tokens = await service.refresh_token(body.refresh_token, redis)
    return APIResponse(data=tokens.model_dump())
```

- [ ] **Step 2: Write endpoints/user.py**

```python
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/users", tags=["Users"])
service = UserService()


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> APIResponse:
    user = await service.get_me(current_user.id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.get("")
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
) -> APIResponse:
    params = PageParams(page=page, page_size=page_size)
    result = await service.get_user_list(params, username, email, status)
    items = [UserResponse.model_validate(u) for u in result.items]
    return APIResponse(data=result.model_dump() | {"items": [i.model_dump() for i in items]})


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    user = await service.get_user(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("")
async def create_user(
    body: UserCreate,
    current_user: Annotated[User, Depends(require_role("admin"))],
) -> APIResponse:
    user = await service.create_user(body)
    return APIResponse(data=UserResponse.model_validate(user))


@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    user = await service.update_user(user_id, body)
    return APIResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_role("admin"))],
) -> APIResponse:
    await service.delete_user(user_id)
    return APIResponse(message="User deleted")
```

- [ ] **Step 3: Write api/v1/router.py**

```python
from fastapi import APIRouter

from app.api.v1.endpoints import auth, user

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(user.router)
```

- [ ] **Step 4: Write middleware/auth.py**

```python
import time

from fastapi import Request
from loguru import logger


async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
    return response
```

- [ ] **Step 5: Write app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.exceptions import global_exception_handler, AppException
from app.database.mongodb import init_db
from app.database.redis import init_redis, close_redis
from app.middleware.auth import request_logging_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}...")
    await init_db()
    await init_redis()
    yield
    await close_redis()
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_logging_middleware)

app.add_exception_handler(AppException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(v1_router)
```

---

### Task 9: Tests

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Create: `backend/tests/test_user.py`

- [ ] **Step 1: Write tests/conftest.py**

```python
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from app.database.redis import redis_client
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_redis():
    redis_client = Redis.from_url("redis://localhost:6379", decode_responses=True)
    yield redis_client
    await redis_client.flushdb()
    await redis_client.close()
```

- [ ] **Step 2: Write tests/test_auth.py**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(async_client: AsyncClient):
    payload = {"username": "testuser", "email": "test@example.com", "password": "Test1234"}
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_duplicate(async_client: AsyncClient):
    payload = {"username": "dupuser", "email": "dup@example.com", "password": "Test1234"}
    await async_client.post("/api/v1/auth/register", json=payload)
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400
    assert resp.json()["code"] == 10002


@pytest.mark.asyncio
async def test_login(async_client: AsyncClient):
    reg = {"username": "loginuser", "email": "login@example.com", "password": "Pass1234"}
    await async_client.post("/api/v1/auth/register", json=reg)
    resp = await async_client.post("/api/v1/auth/login", json={"username": "loginuser", "password": "Pass1234"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert "access_token" in data["data"]
```

- [ ] **Step 3: Write tests/test_user.py**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(async_client: AsyncClient):
    reg = {"username": "meuser", "email": "me@example.com", "password": "Pass1234"}
    await async_client.post("/api/v1/auth/register", json=reg)
    login_resp = await async_client.post("/api/v1/auth/login", json={"username": "meuser", "password": "Pass1234"})
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "meuser"
```

---

### Task 10: README

**Files:**
- Create: `backend/README.md`

- [ ] **Step 1: Write README.md**

```markdown
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

## Project Structure

See [AGENTS.md](../AGENTS.md) for full details.

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
```
