# 代码生成功能设计文档

## 概述

为 FastAPI + MongoDB (Beanie ODM) 后端提供代码生成能力，类似若依的代码生成功能，但适配 Beanie/Python 生态。

用户通过可视化页面配置实体字段，一键生成 Model → Schema → Repository → Service → Endpoint 五层代码。

## 技术选型

**Jinja2 模板引擎** — 为每层代码编写 .j2 模板，根据实体配置渲染后写入文件。

## 核心数据流

```
用户操作                         系统行为
─────────                       ─────────
1. 打开"代码生成"页面          → GET /api/v1/gen/models
                                扫描 app/models/ 下 Beanie 类
2. 选择实体点"导入"            → POST /api/v1/gen/import/{name}
                                解析字段 → 创建 GenTemplate 记录
3. 编辑字段配置                 → PUT /api/v1/gen/templates/:id
                                修改 label/is_list/is_query 等
4. 点击"生成代码"              → POST /api/v1/gen/templates/:id/generate
                                渲染模板 → 写入文件
                                返回文件列表
```

## GenTemplate 数据模型

### GenField（嵌入式 Pydantic BaseModel）

```python
class GenField(BaseModel):
    field_name: str              # 字段名 username
    field_type: str              # Python 类型 str | Optional[str] | int
    label: str = ""              # 中文名 "用户名"
    is_pk: bool = False          # 是否主键
    is_required: bool = False    # 是否必填
    is_list: bool = True         # 列表页显示
    is_query: bool = False       # 支持搜索
    is_form: bool = True         # 表单显示
    query_type: str = "like"     # like / exact / gt / lt / between
    form_type: str = "input"     # input / textarea / select / datetime
    sort: int = 0                # 排序号
    remark: Optional[str] = None
```

### GenTemplate（Beanie Document）

```python
class GenTemplate(Document):
    id: str
    entity_name: str              # User（大驼峰）
    entity_name_cn: str           # "用户"
    module_name: str = "system"
    table_name: str               # "users"（MongoDB 集合名）
    fields: list[GenField] = []
    status: int = 1               # 0=草稿, 1=已配置, 2=已生成
    remark: Optional[str] = None
    created_at: int
    updated_at: int

    class Settings:
        name = "gen_templates"
```

### 字段配置对生成的影响

| 配置 | 影响 |
|---|---|
| `is_pk=True` | Model 中生成 `id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")` |
| `is_list=True` | Endpoint 列表响应包含此字段 |
| `is_query=True` | Service 的 get_list 中添加过滤条件 `query_type` 控制 like / exact |
| `is_form=True` | Schema 的 Create/Update 中包含此字段 |

## 导入机制

区别于若依的数据库表导入，这里从 Beanie Model 类反射导入：

```python
# 使用 Pydantic v2 的 model_fields 反射
for field_name, field_info in User.model_fields.items():
    if field_name in ("id", "created_at", "updated_at"):
        continue  # 排除系统字段
    gen_field = GenField(
        field_name=field_name,
        field_type=str(field_info.annotation),
        is_required="Optional" not in str(field_info.annotation),
        is_pk=(field_name == "id"),
    )
```

导入后状态为"草稿"，用户可在 UI 中调整字段配置。

## 代码生成引擎

### 目录结构

```
backend/app/generators/
├── templates/
│   ├── model.py.j2
│   ├── schema.py.j2
│   ├── repository.py.j2
│   ├── service.py.j2
│   └── endpoint.py.j2
└── engine.py
```

### 引擎流程

```
engine.py(template: GenTemplate)
  │
  ├── 1. build_context(template)
  │      ├── entity_name / entity_lower / table_name
  │      ├── pk_fields / list_fields / query_fields / form_fields
  │      ├── 自动收集需要的 import
  │      └── permission_key: "system:{module}:{action}"
  │
  ├── 2. 逐个渲染模板
  │      model.py.j2       → app/models/{entity_lower}.py
  │      schema.py.j2      → app/schemas/{entity_lower}.py
  │      repository.py.j2  → app/repositories/{entity_lower}_repository.py
  │      service.py.j2     → app/services/{entity_lower}_service.py
  │      endpoint.py.j2    → app/api/v1/endpoints/{entity_lower}.py
  │
  └── 3. 返回 [{file_path, action: "created"|"overwritten"}]
```

### 模板示例（简化）

**model.py.j2** — 生成 Beanie Document
```
import time
from uuid import uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class {{ entity_name }}(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
{% for f in fields if not f.is_pk %}
    {{ f.field_name }}: {{ f.field_type }}
{% endfor %}
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at: int = Field(default_factory=lambda: int(time.time() * 1000))

    class Settings:
        name = "{{ table_name }}"
```

**repository.py.j2** — 生成 CRUD + 分页查询
```
class {{ entity_name }}Repository:
    @staticmethod
    async def create({{ entity_lower }}: {{ entity_name }}) -> {{ entity_name }}:
        return await {{ entity_lower }}.insert()

    @staticmethod
    async def get_by_id({{ entity_lower }}_id: str) -> Optional[{{ entity_name }}]:
        return await {{ entity_name }}.get({{ entity_lower }}_id)

    @staticmethod
    async def update({{ entity_lower }}_id: str, update_data: dict) -> Optional[{{ entity_name }}]:
        obj = await {{ entity_name }}.get({{ entity_lower }}_id)
        if not obj: return None
        update_data["updated_at"] = int(time.time() * 1000)
        await obj.update({"$set": update_data})
        return await {{ entity_name }}.get({{ entity_lower }}_id)

    @staticmethod
    async def delete({{ entity_lower }}_id: str) -> bool:
        obj = await {{ entity_name }}.get({{ entity_lower }}_id)
        if not obj: return False
        await obj.delete()
        return True

    @staticmethod
    async def get_list(params: PageParams, **filters) -> PageResult:
        query = {}
        {% for f in query_fields %}
        if filters.get("{{ f.field_name }}"):
            query["{{ f.field_name }}"] = {"$regex": filters["{{ f.field_name }}"], "$options": "i"}
        {% endfor %}
        total = await {{ entity_name }}.find(query).count()
        items = await {{ entity_name }}.find(query).skip(...).limit(...).to_list()
        return PageResult(items=items, total=total, ...)
```

**endpoint.py.j2** — 生成 RESTful API
```
router = APIRouter(prefix="/{{ entity_lower }}s", tags=["{{ entity_name_cn }}"])
service = {{ entity_name }}Service()

@router.get("")
async def list_{{ entity_lower }}s(...):
    ...

@router.post("")
async def create_{{ entity_lower }}(...) -> APIResponse:
    ...

@router.get("/{{ entity_lower }}_id}")
async def get_{{ entity_lower }}(...) -> APIResponse:
    ...

@router.put("/{{ entity_lower }}_id}")
async def update_{{ entity_lower }}(...) -> APIResponse:
    ...

@router.delete("/{{ entity_lower }}_id}")
async def delete_{{ entity_lower }}(...) -> APIResponse:
    ...
```

## API 端点

| 方法 | 路径 | 权限标识 | 功能 |
|---|---|---|---|
| GET | /api/v1/gen/models | system:gen:list | 列出 Beanie 类列表 |
| GET | /api/v1/gen/models/{name} | system:gen:list | 查看 Model 字段详情 |
| GET | /api/v1/gen/templates | system:gen:list | 分页查询模板列表 |
| POST | /api/v1/gen/templates | system:gen:create | 手动创建空模板 |
| POST | /api/v1/gen/import/{model_name} | system:gen:create | 从 Model 导入创建模板 |
| GET | /api/v1/gen/templates/{id} | system:gen:list | 查看模板详情 |
| PUT | /api/v1/gen/templates/{id} | system:gen:update | 更新模板 |
| DELETE | /api/v1/gen/templates/{id} | system:gen:delete | 删除模板 |
| POST | /api/v1/gen/templates/{id}/generate | system:gen:generate | 执行生成 |

## 权限标识

```
system:gen:list
system:gen:create
system:gen:update
system:gen:delete
system:gen:generate
```

## 错误处理

| 场景 | 处理方式 |
|---|---|
| entity_name 不合法 | 返回 400，提示名称格式 |
| 字段列表为空 | 返回 400，提示至少需要一个非 pk 字段 |
| 模板不存在 | 返回 GenTemplateNotFoundError(10016) |
| Jinja2 渲染错误 | 返回具体模板文件名 + 行号 |
| 文件写入失败 | 返回具体错误（权限/磁盘） |
| 目标文件已存在 | 记录为 overwritten，不报错 |
| 目录不存在 | 自动创建目录 |

## 集成到现有项目

| 文件 | 改动 |
|---|---|
| `app/main.py` | document_models 加 `GenTemplate` |
| `app/api/v1/router.py` | include_router(gen_template.router) |
| `app/core/exceptions.py` | 新增 GenTemplateNotFoundError(10016) |
| `app/generators/templates/` | 5 个 .j2 模板文件（新建） |
| `app/generators/engine.py` | 生成引擎（新建） |

## 边界情况

- **从零创建**：允许手动创建空 GenTemplate，逐字段添加
- **Model 变更后**：重新导入更新 GenTemplate，再点生成
- **实体名冲突**：生成记录中提示已存在文件，可手动改名
- **代码正确性**：生成器不负责验证，需开发者运行 `ruff` 检查
- **created_at/updated_at**：系统字段自动排除，由模板统一生成
- **`xxx_id` 字段**：自动标记为外键引用，label 设为 "xxx"

## 测试策略

```
tests/test_gen/
├── test_gen_import.py     # 导入引擎：mock Model → 验证字段解析
├── test_gen_generate.py   # 生成引擎：mock GenTemplate → 验证渲染输出
└── test_gen_template.py   # API：完整的模板 CRUD + 生成流程集成测试
```
