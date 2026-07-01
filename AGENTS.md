# AGENTS.md — 项目规范

## 项目概述
企业级 FastAPI + MongoDB 后端，模块化架构。

## 技术栈
- Python 3.12+, FastAPI, Pydantic v2, Uvicorn
- MongoDB 7+, PyMongo, Beanie ODM
- Redis, JWT, bcrypt
- uv (依赖管理)
- Docker, Pytest, Loguru

## 架构规范

### 严格分层（必须遵守）
```
Router → Service → Repository → ODM (Beanie)
```
- **Router**：只做参数校验和返回
- **Service**：只做业务逻辑
- **Repository**：只做 MongoDB CRUD
- **严禁**在 Router 或 Service 中写数据库操作代码

### 代码风格
- 所有 I/O 操作必须使用 `async/await`
- 所有函数签名必须有类型注解
- 文档字符串：Google 风格
- 禁止 `print` — 使用 `loguru`
- 导入顺序：标准库 → 第三方 → 本地（空行分隔）

### 数据模型规范（必须遵守）
- **ID 类型**：所有文档 `_id` 字段使用 `str`，通过 `lambda: str(uuid4())` 生成
  ```python
  id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
  ```
- **外键类型**：所有引用 ID 使用 `str`（如 `company_id: str`、`user_id: str`）
- **时间戳**：所有时间字段使用 `int`（毫秒级 Unix 时间戳），通过 `int(time.time() * 1000)` 生成
  ```python
  created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
  updated_at: int = Field(default_factory=lambda: int(time.time() * 1000))
  ```
- **更新时间**：Repository 层每次 update 必须设置 `update_data["updated_at"] = int(time.time() * 1000)`
- **禁止**在模型或 schema 中使用 `UUID` 类型或 `datetime` 类型

### 统一返回格式（所有接口）
```json
{"code": 0, "message": "success", "data": {}}
```
错误响应使用业务错误码（10001+）。

### API 约定
- 前缀：`/api/v1/`
- 版本号在 URL 路径中
- 鉴权通过 `Depends()` 依赖注入

### Token 与认证
- JWT access_token（短期，TTL 可配置）
- JWT refresh_token（长期，存储在 Redis 中）
- 退出登录时通过 Redis 黑名单实现 Token 吊销
- `get_current_user()` 作为 FastAPI 依赖

### 权限控制
- 权限标识格式：`system:<模块>:<操作>`（如 `system:user:create`）
- `require_permission(key)` 替代旧版 `require_role()`
- 用户通过 `role_ids` 多对多关联角色，角色包含 `permissions`（菜单+按钮权限）

### 测试
- pytest + httpx AsyncClient
- 测试目录 `tests/` 镜像 `app/` 结构
- 文件命名：`test_<模块>.py`
- 尽可能 mock 外部服务（MongoDB、Redis）

### 项目流程
1. 设计 → docs/superpowers/specs/YYYY-MM-DD-<主题>-design.md
2. 实施计划 → 通过 writing-plans skill 执行
3. 无批准设计不得修改代码

## 目录结构
```
backend/
├── app/
│   ├── main.py
│   ├── core/           → 配置、安全、日志、异常
│   ├── api/v1/         → 路由、依赖、端点
│   ├── models/         → Beanie 文档模型
│   ├── schemas/        → Pydantic 校验
│   ├── services/       → 业务逻辑
│   ├── repositories/   → MongoDB CRUD
│   ├── database/       → mongodb.py、redis.py
│   ├── utils/          → response.py、pagination.py
│   ├── middleware/     → 鉴权中间件
│   └── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```
