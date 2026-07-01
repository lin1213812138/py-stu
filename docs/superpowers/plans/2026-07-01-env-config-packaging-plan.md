# 环境配置与打包实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 实现基于 `ENV` 系统变量的动态 `.env.{env}` 文件加载，优化 Docker 构建为多阶段模式。

**架构：** 修改 `app/core/config.py` 的 `__init__` 方法，根据系统环境变量 `ENV` 动态决定加载的 env 文件路径；Dockerfile 拆分为 builder + runtime 两阶段。

**技术栈：** pydantic-settings v2, hatchling, Docker multi-stage, uv

## 全局约束

- `ENV` 必须由系统环境变量注入，不放在 env 文件中
- 降级链：`.env.{ENV}` → `.env` → pydantic-settings 默认值
- 一份构建产物（wheel/镜像）用于所有环境
- Python 3.12+, pydantic-settings>=2.0

---

## 文件结构

| 文件 | 操作 | 职责 |
|---|---|---|
| `app/core/config.py` | 修改 | 动态 env_file 加载 + 降级 |
| `tests/test_config.py` | 创建 | 测试 Settings 环境切换逻辑 |
| `.env.development` | 创建 | 开发环境配置 |
| `.env.test` | 创建 | 测试环境配置 |
| `.env.staging` | 创建 | 预发布配置 |
| `.env.production` | 创建 | 生产环境配置 |
| `.dockerignore` | 创建 | 构建上下文清理 |
| `Dockerfile` | 重写 | 多阶段构建 |
| `docker-compose.yml` | 修改 | 通过 `ENV` 动态切换 env_file |

---

### Task 1: 修改 config.py 实现动态 env_file 加载

**文件：**
- 修改：`app/core/config.py`
- 创建：`tests/test_config.py`

**接口：**
- 消费：现有 `Settings` 类的消费者（`from app.core.config import settings`）——接口不变
- 产出：`Settings` 类构造时根据 `os.getenv("ENV", "development")` 加载 `.env.{ENV}`，不存在则降级到 `.env`

- [ ] **Step 1：创建测试文件**

```python
import os
import pytest
from app.core.config import Settings


@pytest.fixture(autouse=True)
def cleanup_env():
    old = os.environ.get("ENV")
    yield
    if old is None:
        os.environ.pop("ENV", None)
    else:
        os.environ["ENV"] = old


def test_settings_instantiation():
    s = Settings()
    assert isinstance(s, Settings)
    assert s.APP_NAME == "python-stu"


def test_env_fallback_to_development():
    os.environ.pop("ENV", None)
    s = Settings()
    assert s.ENV == "development"


def test_env_override_from_system():
    os.environ["ENV"] = "production"
    s = Settings()
    assert s.ENV == "production"
```

- [ ] **Step 2：运行测试，确认测试框架正常**

```bash
.venv\Scripts\python -m pytest tests/test_config.py -v
```

预期：3 passed（旧代码已能正常实例化 Settings）

- [ ] **Step 3：修改 config.py 实现动态加载**

```python
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "python-stu"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "app"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change-this-in-production"
    JWT_ACCESS_EXPIRE: int = 1800
    JWT_REFRESH_EXPIRE: int = 604800
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs):
        env = os.getenv("ENV", "development")
        env_file = f".env.{env}"
        if not Path(env_file).exists():
            env_file = ".env"
        super().__init__(_env_file=env_file, **kwargs)


settings = Settings()
```

- [ ] **Step 4：运行测试，验证通过**

```bash
.venv\Scripts\python -m pytest tests/test_config.py -v
```

预期：3 passed

- [ ] **Step 5：提交**

```bash
git add app/core/config.py tests/test_config.py
git commit -m "feat: dynamic env_file loading based on ENV system variable"
```

---

### Task 2：创建 .env.development / .env.test / .env.staging / .env.production

**文件：**
- 创建：`.env.development`（从现有 `.env` 复制）
- 创建：`.env.test`
- 创建：`.env.staging`
- 创建：`.env.production`

- [ ] **Step 1：创建 .env.development**（从 `.env` 复制）

```bash
Copy-Item -LiteralPath ".env" -Destination ".env.development"
```

- [ ] **Step 2：创建 .env.test**

内容：
```
APP_NAME=python-stu
ENV=test

MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=app_test

REDIS_URL=redis://localhost:6379

JWT_SECRET=test-secret-key
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["*"]
```

- [ ] **Step 3：创建 .env.staging**

内容：
```
APP_NAME=python-stu
ENV=staging

MONGODB_URL=mongodb://staging-mongo:27017
MONGODB_DATABASE=app

REDIS_URL=redis://staging-redis:6379

JWT_SECRET=staging-secret-key
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["https://staging.example.com"]
```

- [ ] **Step 4：创建 .env.production**

内容：
```
APP_NAME=python-stu
ENV=production

MONGODB_URL=mongodb://prod-mongo:27017
MONGODB_DATABASE=app

REDIS_URL=redis://prod-redis:6379

JWT_SECRET=prod-secret-key
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["https://example.com"]
```

- [ ] **Step 5：验证 Settings 能加载各环境文件**

```bash
$env:ENV="development"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
$env:ENV="test"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
$env:ENV="staging"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
$env:ENV="production"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
```

预期：每个环境输出不同的 `MONGODB_URL`
- development → `localhost`
- test → `localhost`（database 为 `app_test`）
- staging → `staging-mongo:27017`
- production → `prod-mongo:27017`

- [ ] **Step 6：提交**

```bash
git add .env.development .env.test .env.staging .env.production
git commit -m "feat: add environment-specific .env files"
```

---

### Task 3：创建 .dockerignore

**文件：**
- 创建：`.dockerignore`

- [ ] **Step 1：创建 .dockerignore**

```
.venv/
__pycache__/
*.pyc
.git/
.gitignore
logs/
.env
.env.*
dist/
*.egg-info/
.idea/
.pytest_cache/
README.md
```

注意：`.env.*` 排除所有 env 文件——镜像不携带任何环境配置，运行时挂载。

- [ ] **Step 2：提交**

```bash
git add .dockerignore
git commit -m "chore: add .dockerignore for clean Docker builds"
```

---

### Task 4：重写 Dockerfile——多阶段构建

**文件：**
- 重写：`Dockerfile`

- [ ] **Step 1：重写 Dockerfile**

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
RUN uv sync --no-dev --frozen

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

- [ ] **Step 2：验证 Docker build 成功**

```bash
docker build -t python-stu:latest .
```

预期：build 成功，最终镜像大小明显小于单阶段构建

- [ ] **Step 3：提交**

```bash
git add Dockerfile
git commit -m "refactor: multi-stage Docker build for smaller production image"
```

---

### Task 5：更新 docker-compose.yml

**文件：**
- 修改：`docker-compose.yml`

- [ ] **Step 1：更新 docker-compose.yml**

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
      - .env.${ENV:-development}
    environment:
      - ENV=${ENV:-development}
    volumes:
      - .:/app
    depends_on:
      - mongodb
      - redis
    restart: unless-stopped

volumes:
  mongo_data:
```

- [ ] **Step 2：提交**

```bash
git add docker-compose.yml
git commit -m "feat: dynamic env_file in docker-compose via ENV variable"
```
