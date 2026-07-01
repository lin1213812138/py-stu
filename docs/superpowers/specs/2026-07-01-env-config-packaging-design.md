# 环境配置与打包 — 设计规范

**日期：** 2026-07-01
**项目：** python-stu — 企业级 FastAPI + MongoDB 后端

---

## 1. 概述

重构环境变量配置系统，支持四个环境（dev、test、staging、production），并重新设计打包策略以实现多环境部署。设计遵循 12-Factor App 原则：**一份构建产物，运行时配置**。

### 目标
- 基于 `ENV` 系统变量动态加载 `.env.{env}` 文件
- 通过 hatchling 构建 Python wheel 包
- 多阶段 Docker 构建用于生产
- 构建时代码与运行时配置严格分离

### 非目标
- 不在构建时嵌入环境配置（密钥不写入镜像层）
- 不使用环境特定的 Dockerfile（所有环境共用同一个 Dockerfile）

---

## 2. 架构：配置加载

### 流程

```
系统环境设置 ENV=production
         │
         ▼
Settings.__init__() → os.getenv("ENV", "development")
         │
         ▼
pydantic-settings 加载 .env.{ENV}（例如 .env.production）
         │
         ▼
settings 单例携带环境特定的值
```

### 关键规则
- `ENV` 必须通过**系统环境变量**设置（不能放在 env 文件中——否则循环依赖）
- 降级链：`.env.{ENV}` → `.env` → pydantic-settings 默认值
- 系统环境变量始终覆盖文件中的值（pydantic-settings 原生行为）

---

## 3. 文件结构

```
backend/
├── .env                    # 旧版降级（内容同 .env.development）
├── .env.example            # 模板占位值
├── .env.development        # 本地开发（localhost）
├── .env.test               # CI / 自动化测试
├── .env.staging            # 预发布环境
├── .env.production         # 生产环境
├── app/core/config.py      # 修改：动态 env_file 加载
├── Dockerfile              # 重写：多阶段构建
├── docker-compose.yml      # 修改：按 ENV 切换 env_file
├── .dockerignore           # 新增：排除开发产物
└── pyproject.toml          # 不变（hatchling 已配置）
```

### 各环境文件差异

| 变量 | `.env.development` | `.env.test` | `.env.staging` | `.env.production` |
|---|---|---|---|---|
| `MONGODB_URL` | `localhost` | `localhost` | `staging-mongo:27017` | `prod-mongo:27017` |
| `REDIS_URL` | `localhost` | `localhost` | `staging-redis:6379` | `prod-redis:6379` |
| `JWT_SECRET` | `dev-secret` | `test-secret` | `staging-secret` | `prod-secret` |
| `JWT_ACCESS_EXPIRE` | `1800` | `1800` | `1800` | `1800` |
| `JWT_REFRESH_EXPIRE` | `604800` | `604800` | `604800` | `604800` |
| `CORS_ORIGINS` | `["*"]` | `["*"]` | `["https://staging.example.com"]` | `["https://example.com"]` |

---

## 4. Config 模块改动

**文件：** `backend/app/core/config.py`

### 当前（修改前）：
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    ...
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### 修改后：
```python
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

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

- `ENV` 从系统环境读取，默认 `"development"`
- 主 env 文件：`.env.{ENV}`，降级到 `.env`
- 所有密钥/配置保留在文件中，从不进入镜像层

---

## 5. 打包策略

### 5.1 Python Wheel

```bash
hatch build    # 生成 dist/python_stu-0.1.0-py3-none-any.whl
```

- 所有环境共用一个 wheel
- Wheel 只包含 `app/` 包 — **不含 `.env.*` 文件**
- 部署方式：`pip install wheel` + 运行时挂载/创建 `.env.{env}`

### 5.2 Docker 多阶段构建

```dockerfile
# 阶段 1：构建器
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev --frozen
COPY . .
RUN uv build --wheel --out-dir /dist

# 阶段 2：运行时
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

与当前的区别：
- **多阶段：** 构建器 + 运行时，最终镜像更小
- **CMD 中不含 `--reload`：** 仅用于开发
- **非 root 用户：** 以 `appuser`（uid 1000）运行
- **uv build → wheel：** 正确隔离构建
- **最终镜像不含 dev 依赖**

### 5.3 Docker Compose 更新

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

实际部署示例：
```bash
# 开发环境（默认，无需额外参数）
docker compose up

# 预发布环境
ENV=staging docker compose up

# 生产环境
ENV=production docker compose up -d
```

---

## 6. 边界情况

| 场景 | 行为 |
|---|---|
| `ENV` 未设置，`.env.development` 不存在 | 降级到 `.env`，然后是 pydantic-settings 默认值 |
| `ENV=production`，`.env.production` 不存在 | 仅使用系统环境变量 + 默认值（K8s 模式） |
| 系统环境变量和 env 文件都设置了同一个键 | 系统环境变量优先（pydantic-settings 原生行为） |
| `ENV` 包含意外值（如 `dev2`） | 如果 `.env.dev2` 存在则加载，否则降级到 `.env` |
| Wheel 安装后，没有 `.env.*` 文件 | 所有设置回退到类默认值 |

---

## 7. 需创建/修改的文件

| 文件 | 操作 | 用途 |
|---|---|---|
| `.env.development` | 创建 | 开发环境配置（从现有 `.env` 复制） |
| `.env.test` | 创建 | CI/测试环境配置 |
| `.env.staging` | 创建 | 预发布环境配置 |
| `.env.production` | 创建 | 生产环境配置 |
| `.dockerignore` | 创建 | 排除 `.venv`、`__pycache__`、`logs`、`.git` |
| `app/core/config.py` | 修改 | 动态 env_file 加载 + 降级 |
| `Dockerfile` | 重写 | 多阶段构建 |
| `docker-compose.yml` | 修改 | 通过 `ENV` 动态切换 env_file |

无需修改：
- `pyproject.toml`（hatchling 已配置）
- `.gitignore`（`.env` 已忽略；`.env.*.example` 可被跟踪）
- 任何 router / service / repository 代码（settings 消费方式不变）

---

## 8. 未来考虑

- **密钥管理服务**（Vault / AWS Parameter Store）：后续可作为 `Settings` 的自定义数据源添加，不改动消费端代码
- **`.env.example` 按环境提供**：可选 `.env.development.example`、`.env.production.example` 用于新成员 onboarding
- **CI 集成**：测试环境可注入 `ENV=test`，通过 CI secrets 挂载 `.env.test`
