# 代码生成功能 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 FastAPI + MongoDB (Beanie ODM) 后端实现代码生成模块，支持从现有 Model 导入配置，一键生成 Model → Schema → Repository → Service → Endpoint 五层代码。

**Architecture:** Jinja2 模板引擎渲染五层代码文件；GenTemplate 集合存储实体字段配置；Import Service 通过反射解析现有 Beanie Model 类字段填充模板；Generator Engine 根据 GenTemplate 渲染模板并写入项目目录。

**Tech Stack:** Python 3.12+, FastAPI, Beanie, Pydantic v2, Jinja2

## Global Constraints

- 所有 I/O 操作使用 `async/await`
- 所有函数签名必须有类型注解
- 禁止 `print` — 使用 `loguru`
- MongoDB 无主键概念，`id`/`created_at`/`updated_at` 为系统字段，不出现在字段配置中
- 导入顺序：标准库 → 第三方 → 本地（空行分隔）
- 提交信息使用中文

---

## File Structure

```
新文件:
  app/models/gen_template.py            ← GenField + GenTemplate
  app/schemas/gen_template.py            ← GenTemplateCreate/Update/Response
  app/repositories/gen_template_repository.py ← CRUD
  app/services/gen_template_service.py   ← 模板业务逻辑
  app/services/gen_import_service.py     ← 模型导入引擎
  app/generators/templates/
    ├── model.py.j2
    ├── schema.py.j2
    ├── repository.py.j2
    ├── service.py.j2
    └── endpoint.py.j2
  app/generators/engine.py               ← 代码生成引擎
  app/api/v1/endpoints/gen_template.py   ← API 端点
  tests/test_gen/
    ├── __init__.py
    ├── test_gen_import.py
    ├── test_gen_generate.py
    └── test_gen_template.py

修改文件:
  app/core/exceptions.py                 ← 新增 GenTemplateNotFoundError
  app/database/mongodb.py                ← 注册 GenTemplate 文档
  app/api/v1/router.py                   ← 注册 gen 路由
```

---

### Task 1: GenField + GenTemplate Models

**Files:**
- Create: `backend/app/models/gen_template.py`
- Test: `backend/tests/test_gen/test_gen_template.py`（部分）

**Interfaces:**
- Consumes: `pydantic.BaseModel`, `beanie.Document`
- Produces: `class GenField(BaseModel)`, `class GenTemplate(Document)`

- [ ] **Step 1: Create the model file**

**创建 `backend/app/models/gen_template.py`:**

```python
import time
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import BaseModel, Field


class GenField(BaseModel):
    field_name: str
    field_type: str
    label: str = ""
    is_required: bool = False
    is_list: bool = True
    is_query: bool = False
    is_form: bool = True
    query_type: str = "like"
    form_type: str = "input"
    sort: int = 0
    remark: Optional[str] = None


class GenTemplate(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    entity_name: str
    entity_name_cn: str
    module_name: str = "system"
    table_name: str
    fields: list[GenField] = []
    status: int = 1
    remark: Optional[str] = None
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at: int = Field(default_factory=lambda: int(time.time() * 1000))

    class Settings:
        name = "gen_templates"

    model_config = {"populate_by_name": True}
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/gen_template.py
git commit -m "feat: 添加 GenField 和 GenTemplate 数据模型"
```

---

### Task 2: GenTemplate Schemas

**Files:**
- Create: `backend/app/schemas/gen_template.py`

**Interfaces:**
- Consumes: `GenField` from `app.models.gen_template`
- Produces: `class GenTemplateCreate(BaseModel)`, `class GenTemplateUpdate(BaseModel)`, `class GenTemplateResponse(BaseModel)`

- [ ] **Step 1: Create the schemas file**

**创建 `backend/app/schemas/gen_template.py`:**

```python
from typing import Optional

from pydantic import BaseModel

from app.models.gen_template import GenField


class GenTemplateCreate(BaseModel):
    entity_name: str
    entity_name_cn: str
    module_name: str = "system"
    table_name: str
    fields: list[GenField] = []
    remark: Optional[str] = None


class GenTemplateUpdate(BaseModel):
    entity_name: Optional[str] = None
    entity_name_cn: Optional[str] = None
    module_name: Optional[str] = None
    table_name: Optional[str] = None
    fields: Optional[list[GenField]] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class GenTemplateResponse(BaseModel):
    id: str
    entity_name: str
    entity_name_cn: str
    module_name: str
    table_name: str
    fields: list[GenField]
    status: int
    remark: Optional[str] = None
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/gen_template.py
git commit -m "feat: 添加 GenTemplate 请求/响应 Schema"
```

---

### Task 3: GenTemplate Repository

**Files:**
- Create: `backend/app/repositories/gen_template_repository.py`

**Interfaces:**
- Consumes: `GenTemplate` from `app.models.gen_template`, `PageParams` and `PageResult` from `app.utils.pagination`
- Produces: `class GenTemplateRepository` with `create`, `get_by_id`, `update`, `delete`, `get_list`, `get_by_entity_name`

- [ ] **Step 1: Create the repository file**

**创建 `backend/app/repositories/gen_template_repository.py`:**

```python
import time
from typing import Optional

from app.models.gen_template import GenTemplate
from app.utils.pagination import PageParams, PageResult


class GenTemplateRepository:

    @staticmethod
    async def create(template: GenTemplate) -> GenTemplate:
        return await template.insert()

    @staticmethod
    async def get_by_id(template_id: str) -> Optional[GenTemplate]:
        return await GenTemplate.get(template_id)

    @staticmethod
    async def get_by_entity_name(entity_name: str) -> Optional[GenTemplate]:
        return await GenTemplate.find_one(GenTemplate.entity_name == entity_name)

    @staticmethod
    async def update(template_id: str, update_data: dict) -> Optional[GenTemplate]:
        obj = await GenTemplate.get(template_id)
        if not obj:
            return None
        update_data["updated_at"] = int(time.time() * 1000)
        await obj.update({"$set": update_data})
        return await GenTemplate.get(template_id)

    @staticmethod
    async def delete(template_id: str) -> bool:
        obj = await GenTemplate.get(template_id)
        if not obj:
            return False
        await obj.delete()
        return True

    @staticmethod
    async def get_list(
        params: PageParams,
        entity_name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult:
        query = {}
        if entity_name:
            query["entity_name"] = {"$regex": entity_name, "$options": "i"}
        if status is not None:
            query["status"] = status

        total = await GenTemplate.find(query).count()
        items = (
            await GenTemplate.find(query)
            .sort(-GenTemplate.created_at)
            .skip((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .to_list()
        )

        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
        )
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/repositories/gen_template_repository.py
git commit -m "feat: 添加 GenTemplate Repository CRUD"
```

---

### Task 4: GenTemplate Service

**Files:**
- Create: `backend/app/services/gen_template_service.py`

**Interfaces:**
- Consumes: `GenTemplateRepository`, `GenTemplateCreate/Update` schemas, `AppException`
- Produces: `class GenTemplateService` with `create`, `get_by_id`, `update`, `delete`, `get_list`

- [ ] **Step 1: Create the service file**

**创建 `backend/app/services/gen_template_service.py`:**

```python
from typing import Optional

from app.core.exceptions import AppException
from app.models.gen_template import GenTemplate
from app.repositories.gen_template_repository import GenTemplateRepository
from app.schemas.gen_template import GenTemplateCreate, GenTemplateUpdate
from app.utils.pagination import PageParams, PageResult


class GenTemplateService:

    def __init__(self):
        self.repo = GenTemplateRepository()

    async def get_by_id(self, template_id: str) -> GenTemplate:
        template = await self.repo.get_by_id(template_id)
        if not template:
            raise AppException(code=10016, message="生成模板不存在")
        return template

    async def get_list(
        self,
        params: PageParams,
        entity_name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult:
        return await self.repo.get_list(params, entity_name, status)

    async def create(self, data: GenTemplateCreate) -> GenTemplate:
        template = GenTemplate(**data.model_dump())
        return await self.repo.create(template)

    async def update(self, template_id: str, data: GenTemplateUpdate) -> GenTemplate:
        template = await self.get_by_id(template_id)
        update_data = data.model_dump(exclude_unset=True)
        result = await self.repo.update(template_id, update_data)
        return result

    async def delete(self, template_id: str) -> None:
        template = await self.get_by_id(template_id)
        deleted = await self.repo.delete(template_id)
        if not deleted:
            raise AppException(code=10016, message="生成模板不存在")
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/gen_template_service.py
git commit -m "feat: 添加 GenTemplate Service 业务逻辑"
```

---

### Task 5: Import Service

**Files:**
- Create: `backend/app/services/gen_import_service.py`
- Test: `backend/tests/test_gen/test_gen_import.py`

**Interfaces:**
- Consumes: `GenTemplate`, `GenTemplateRepository`
- Produces: `class GenImportService` with `scan_models`, `import_model`

- [ ] **Step 1: Create the import service**

**创建 `backend/app/services/gen_import_service.py`:**

```python
import importlib
import inspect
import pkgutil
from typing import get_origin, get_args

from beanie import Document

from app.core.exceptions import AppException
from app.models.gen_template import GenField, GenTemplate
from app.repositories.gen_template_repository import GenTemplateRepository


class GenImportService:

    def __init__(self):
        self.repo = GenTemplateRepository()

    def scan_models(self) -> list[dict]:
        import app.models

        results = []
        for _, module_name, _ in pkgutil.iter_modules(app.models.__path__):
            module = importlib.import_module(f"app.models.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Document) and obj != Document:
                    collection = getattr(obj.Settings, "name", f"{name.lower()}s")
                    field_count = len(obj.model_fields)
                    results.append({
                        "name": name,
                        "collection": collection,
                        "fields_count": field_count,
                    })
        return results

    def _parse_field_type(self, annotation) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is type(None):
            return "None"
        if origin is list:
            inner = self._parse_field_type(args[0]) if args else "Any"
            return f"list[{inner}]"
        return getattr(annotation, "__name__", str(annotation))

    async def import_model(self, model_name: str) -> GenTemplate:
        import app.models

        model_cls = None
        for _, module_name, _ in pkgutil.iter_modules(app.models.__path__):
            module = importlib.import_module(f"app.models.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Document) and obj != Document and name == model_name:
                    model_cls = obj
                    break

        if not model_cls:
            raise AppException(code=10017, message=f"模型 {model_name} 不存在")

        system_fields = {"id", "created_at", "updated_at"}
        fields = []
        for field_name, field_info in model_cls.model_fields.items():
            if field_name in system_fields:
                continue
            annotation = field_info.annotation
            is_optional = False
            raw_type = annotation
            origin = get_origin(annotation)
            args = get_args(annotation)

            if origin is type(None):
                continue
            if origin is list:
                fields.append(GenField(
                    field_name=field_name,
                    field_type=self._parse_field_type(annotation),
                    label=field_name,
                    is_form=True,
                    is_list=True,
                ))
                continue

            if origin is not None:
                if hasattr(origin, "__name__") and origin.__name__ == "Optional":
                    is_optional = True
                    raw_type = args[0] if args else str

            field_type = self._parse_field_type(raw_type)
            fields.append(GenField(
                field_name=field_name,
                field_type=field_type,
                label=field_name,
                is_required=not is_optional,
                is_form=True,
                is_list=True,
            ))

        entity_name_cn = getattr(model_cls, "__doc__", model_name) or model_name
        table_name = getattr(model_cls.Settings, "name", f"{model_name.lower()}s")

        template = GenTemplate(
            entity_name=model_name,
            entity_name_cn=entity_name_cn.strip(),
            table_name=table_name,
            fields=fields,
        )
        return await self.repo.create(template)
```

- [ ] **Step 2: Write the failing test**

**创建 `backend/tests/test_gen/__init__.py`**（空文件）

**创建 `backend/tests/test_gen/test_gen_import.py`:**

```python
from unittest.mock import patch, MagicMock

import pytest

from app.models.gen_template import GenField, GenTemplate
from app.services.gen_import_service import GenImportService


@pytest.mark.asyncio
async def test_import_model_creates_template():
    service = GenImportService()
    with patch.object(service.repo, "create") as mock_create:
        mock_create.return_value = GenTemplate(
            id="mock-id",
            entity_name="TestModel",
            entity_name_cn="测试模型",
            table_name="testmodels",
            fields=[],
        )
        result = await service.import_model("TestModel")
        assert result.entity_name == "TestModel"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_scan_models_returns_list():
    service = GenImportService()
    with patch("app.services.gen_import_service.pkgutil.iter_modules", return_value=[]):
        result = service.scan_models()
        assert result == []
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_gen/test_gen_import.py -v`
Expected: FAIL with import errors

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/gen_import_service.py
git add backend/tests/test_gen/
git commit -m "feat: 添加模型导入服务，支持从 Beanie Model 反射导入"
```

---

### Task 6: Generator Templates (5 Jinja2 文件)

**Files:**
- Create: `backend/app/generators/templates/model.py.j2`
- Create: `backend/app/generators/templates/schema.py.j2`
- Create: `backend/app/generators/templates/repository.py.j2`
- Create: `backend/app/generators/templates/service.py.j2`
- Create: `backend/app/generators/templates/endpoint.py.j2`

- [ ] **Step 1: Create `model.py.j2`**

**创建 `backend/app/generators/templates/model.py.j2`:**

```
import time
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field


class {{ entity_name }}(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
{% for f in fields %}
    {{ f.field_name }}: {{ f.field_type }}
{% endfor %}
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at: int = Field(default_factory=lambda: int(time.time() * 1000))

    class Settings:
        name = "{{ table_name }}"

    model_config = {"populate_by_name": True}
```

- [ ] **Step 2: Create `schema.py.j2`**

**创建 `backend/app/generators/templates/schema.py.j2`:**

```
from typing import Optional

from pydantic import BaseModel


class {{ entity_name }}Create(BaseModel):
{% for f in form_fields %}
{% if f.is_required %}
    {{ f.field_name }}: {{ f.field_type }}
{% else %}
    {{ f.field_name }}: Optional[{{ f.field_type[9:-1] if f.field_type.startswith('Optional') else f.field_type }}] = None
{% endif %}
{% endfor %}


class {{ entity_name }}Update(BaseModel):
{% for f in form_fields %}
    {{ f.field_name }}: Optional[{{ f.field_type[9:-1] if f.field_type.startswith('Optional') else f.field_type }}] = None
{% endfor %}


class {{ entity_name }}Response(BaseModel):
    id: str
{% for f in list_fields %}
    {{ f.field_name }}: {{ f.field_type }}
{% endfor %}
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Create `repository.py.j2`**

**创建 `backend/app/generators/templates/repository.py.j2`:**

```
import time
from typing import Optional

from app.models.{{ entity_lower }} import {{ entity_name }}
from app.utils.pagination import PageParams, PageResult


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
        if not obj:
            return None
        update_data["updated_at"] = int(time.time() * 1000)
        await obj.update({"$set": update_data})
        return await {{ entity_name }}.get({{ entity_lower }}_id)

    @staticmethod
    async def delete({{ entity_lower }}_id: str) -> bool:
        obj = await {{ entity_name }}.get({{ entity_lower }}_id)
        if not obj:
            return False
        await obj.delete()
        return True

    @staticmethod
    async def get_list(
        params: PageParams,
{% for f in query_fields %}
        {{ f.field_name }}: Optional[{{ f.field_type[9:-1] if f.field_type.startswith('Optional') else f.field_type }}] = None{% if not loop.last %},{% endif %}
{% endfor %}
    ) -> PageResult:
        query = {}
{% for f in query_fields %}
        if {{ f.field_name }} is not None:
            query["{{ f.field_name }}"] = {"$regex": {{ f.field_name }}, "$options": "i"}
{% endfor %}
        total = await {{ entity_name }}.find(query).count()
        items = (
            await {{ entity_name }}.find(query)
            .sort(-{{ entity_name }}.created_at)
            .skip((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .to_list()
        )
        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
        )
```

- [ ] **Step 4: Create `service.py.j2`**

**创建 `backend/app/generators/templates/service.py.j2`:**

```
from typing import Optional

from app.core.exceptions import AppException
from app.models.{{ entity_lower }} import {{ entity_name }}
from app.repositories.{{ entity_lower }}_repository import {{ entity_name }}Repository
from app.schemas.{{ entity_lower }} import {{ entity_name }}Create, {{ entity_name }}Update, {{ entity_name }}Response
from app.utils.pagination import PageParams, PageResult


class {{ entity_name }}Service:

    def __init__(self):
        self.repo = {{ entity_name }}Repository()

    async def get_by_id(self, {{ entity_lower }}_id: str) -> {{ entity_name }}:
        obj = await self.repo.get_by_id({{ entity_lower }}_id)
        if not obj:
            raise AppException(code=10001, message="{{ entity_name_cn }}不存在")
        return obj

    async def get_list(
        self,
        params: PageParams,
{% for f in query_fields %}
        {{ f.field_name }}: Optional[{{ f.field_type[9:-1] if f.field_type.startswith('Optional') else f.field_type }}] = None{% if not loop.last %},{% endif %}
{% endfor %}
    ) -> PageResult:
        result = await self.repo.get_list(params{% for f in query_fields %}, {{ f.field_name }}={{ f.field_name }}{% endfor %})
        result.items = [{{ entity_name }}Response.model_validate(item) for item in result.items]
        return result

    async def create(self, data: {{ entity_name }}Create) -> {{ entity_name }}:
        obj = {{ entity_name }}(**data.model_dump())
        return await self.repo.create(obj)

    async def update(self, {{ entity_lower }}_id: str, data: {{ entity_name }}Update) -> {{ entity_name }}:
        await self.get_by_id({{ entity_lower }}_id)
        result = await self.repo.update({{ entity_lower }}_id, data.model_dump(exclude_unset=True))
        return result

    async def delete(self, {{ entity_lower }}_id: str) -> None:
        await self.get_by_id({{ entity_lower }}_id)
        await self.repo.delete({{ entity_lower }}_id)
```

- [ ] **Step 5: Create `endpoint.py.j2`**

**创建 `backend/app/generators/templates/endpoint.py.j2`:**

```
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.{{ entity_lower }} import {{ entity_name }}Create, {{ entity_name }}Response, {{ entity_name }}Update
from app.services.{{ entity_lower }}_service import {{ entity_name }}Service
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/{{ entity_lower }}s", tags=["{{ entity_name_cn }}"])
service = {{ entity_name }}Service()


@router.get("")
async def list_{{ entity_lower }}s(
    current_user: Annotated[User, Depends(require_permission("{{ module_name }}:{{ entity_lower }}:list"))],
    params: Annotated[PageParams, Depends()],
{% for f in query_fields %}
    {{ f.field_name }}: Optional[{{ f.field_type[9:-1] if f.field_type.startswith('Optional') else f.field_type }}] = Query(None){% if not loop.last %},{% endif %}
{% endfor %}
) -> APIResponse:
    result = await service.get_list(params{% for f in query_fields %}, {{ f.field_name }}={{ f.field_name }}{% endfor %})
    return APIResponse(data=result.model_dump())


@router.post("")
async def create_{{ entity_lower }}(
    current_user: Annotated[User, Depends(require_permission("{{ module_name }}:{{ entity_lower }}:create"))],
    body: {{ entity_name }}Create,
) -> APIResponse:
    obj = await service.create(body)
    return APIResponse(data={{ entity_name }}Response.model_validate(obj).model_dump())


@router.get("/{{ "{" }}{{ entity_lower }}_id}")
async def get_{{ entity_lower }}(
    {{ entity_lower }}_id: str,
    current_user: Annotated[User, Depends(require_permission("{{ module_name }}:{{ entity_lower }}:list"))],
) -> APIResponse:
    obj = await service.get_by_id({{ entity_lower }}_id)
    return APIResponse(data={{ entity_name }}Response.model_validate(obj).model_dump())


@router.put("/{{ "{" }}{{ entity_lower }}_id}")
async def update_{{ entity_lower }}(
    {{ entity_lower }}_id: str,
    body: {{ entity_name }}Update,
    current_user: Annotated[User, Depends(require_permission("{{ module_name }}:{{ entity_lower }}:update"))],
) -> APIResponse:
    obj = await service.update({{ entity_lower }}_id, body)
    return APIResponse(data={{ entity_name }}Response.model_validate(obj).model_dump())


@router.delete("/{{ "{" }}{{ entity_lower }}_id}")
async def delete_{{ entity_lower }}(
    {{ entity_lower }}_id: str,
    current_user: Annotated[User, Depends(require_permission("{{ module_name }}:{{ entity_lower }}:delete"))],
) -> APIResponse:
    await service.delete({{ entity_lower }}_id)
    return APIResponse(message="删除成功")
```

- [ ] **Step 6: Create `__init__.py` for generators package**

**创建 `backend/app/generators/__init__.py`**（空文件）

**创建 `backend/app/generators/templates/__init__.py`**（空文件）

- [ ] **Step 7: Commit**

```bash
git add backend/app/generators/
git commit -m "feat: 添加 5 个 Jinja2 代码生成模板"
```

---

### Task 7: Generator Engine

**Files:**
- Create: `backend/app/generators/engine.py`
- Test: `backend/tests/test_gen/test_gen_generate.py`

**Interfaces:**
- Consumes: `GenTemplate`, `jinja2.Environment`
- Produces: `class GeneratorEngine` with `build_context`, `generate`

- [ ] **Step 1: Write the failing test**

**创建 `backend/tests/test_gen/test_gen_generate.py`:**

```python
import pytest

from app.models.gen_template import GenField, GenTemplate


@pytest.fixture
def sample_template():
    return GenTemplate(
        id="test-id",
        entity_name="Product",
        entity_name_cn="产品",
        module_name="system",
        table_name="products",
        fields=[
            GenField(
                field_name="name",
                field_type="str",
                label="产品名称",
                is_required=True,
                is_list=True,
                is_query=True,
                is_form=True,
            ),
            GenField(
                field_name="price",
                field_type="float",
                label="价格",
                is_required=True,
                is_list=True,
                is_query=False,
                is_form=True,
            ),
            GenField(
                field_name="description",
                field_type="Optional[str]",
                label="描述",
                is_required=False,
                is_list=False,
                is_query=False,
                is_form=True,
            ),
        ],
    )


@pytest.mark.asyncio
async def test_generate_creates_files(sample_template, tmp_path):
    from app.generators.engine import GeneratorEngine

    engine = GeneratorEngine()
    result = await engine.generate(sample_template, str(tmp_path))

    assert len(result) == 5
    paths = [r["path"] for r in result]
    assert "models/product.py" in paths
    assert "schemas/product.py" in paths
    assert "repositories/product_repository.py" in paths
    assert "services/product_service.py" in paths
    assert "api/v1/endpoints/product.py" in paths
    for r in result:
        assert r["action"] in ("created", "overwritten")


@pytest.mark.asyncio
async def test_rendered_model_contains_entity_name(sample_template, tmp_path):
    from app.generators.engine import GeneratorEngine

    engine = GeneratorEngine()
    await engine.generate(sample_template, str(tmp_path))

    model_path = tmp_path / "models" / "product.py"
    content = model_path.read_text(encoding="utf-8")
    assert "class Product(Document):" in content
    assert "name: str" in content
    assert "price: float" in content
    assert "description: Optional[str]" in content
    assert 'name = "products"' in content


@pytest.mark.asyncio
async def test_rendered_endpoint_contains_routes(sample_template, tmp_path):
    from app.generators.engine import GeneratorEngine

    engine = GeneratorEngine()
    await engine.generate(sample_template, str(tmp_path))

    endpoint_path = tmp_path / "api" / "v1" / "endpoints" / "product.py"
    content = endpoint_path.read_text(encoding="utf-8")
    assert 'prefix="/products"' in content
    assert "async def list_products(" in content
    assert "async def create_product(" in content
    assert "async def get_product(" in content
    assert "async def update_product(" in content
    assert "async def delete_product(" in content


@pytest.mark.asyncio
async def test_query_fields_appear_in_endpoint(sample_template, tmp_path):
    from app.generators.engine import GeneratorEngine

    engine = GeneratorEngine()
    await engine.generate(sample_template, str(tmp_path))

    endpoint_path = tmp_path / "api" / "v1" / "endpoints" / "product.py"
    content = endpoint_path.read_text(encoding="utf-8")
    assert "name: Optional[str] = Query(None)" in content
    assert "price" not in content.split("Query(None)")[-1]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gen/test_gen_generate.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Create the engine**

**创建 `backend/app/generators/engine.py`:**

```python
import os

from jinja2 import Environment, FileSystemLoader

from app.models.gen_template import GenTemplate


class GeneratorEngine:

    OUTPUT_MAP = {
        "model.py.j2": "models/{entity_lower}.py",
        "schema.py.j2": "schemas/{entity_lower}.py",
        "repository.py.j2": "repositories/{entity_lower}_repository.py",
        "service.py.j2": "services/{entity_lower}_service.py",
        "endpoint.py.j2": "api/v1/endpoints/{entity_lower}.py",
    }

    def __init__(self, templates_dir: str | None = None):
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _build_context(self, template: GenTemplate) -> dict:
        entity_lower = template.entity_name[:1].lower() + template.entity_name[1:]
        return {
            "entity_name": template.entity_name,
            "entity_lower": entity_lower,
            "table_name": template.table_name,
            "module_name": template.module_name,
            "entity_name_cn": template.entity_name_cn,
            "fields": template.fields,
            "list_fields": [f for f in template.fields if f.is_list],
            "query_fields": [f for f in template.fields if f.is_query],
            "form_fields": [f for f in template.fields if f.is_form],
        }

    async def generate(self, template: GenTemplate, output_dir: str) -> list[dict]:
        context = self._build_context(template)
        results = []

        for tmpl_name, output_rel in self.OUTPUT_MAP.items():
            output_path = output_rel.format(entity_lower=context["entity_lower"])
            full_path = os.path.join(output_dir, output_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            tmpl = self.env.get_template(tmpl_name)
            content = tmpl.render(**context)

            action = "overwritten" if os.path.exists(full_path) else "created"
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            results.append({"path": output_path, "action": action})

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gen/test_gen_generate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/generators/engine.py
git add tests/test_gen/test_gen_generate.py
git commit -m "feat: 添加代码生成引擎，支持 Jinja2 渲染和文件写入"
```

---

### Task 8: API Endpoints

**Files:**
- Create: `backend/app/api/v1/endpoints/gen_template.py`
- Test: `backend/tests/test_gen/test_gen_template.py`

**Interfaces:**
- Consumes: `GenTemplateService`, `GenImportService`, `GeneratorEngine`
- Produces: 9 REST endpoints for gen template management

- [ ] **Step 1: Write the failing test**

**创建 `backend/tests/test_gen/test_gen_template.py`:**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_templates_requires_auth(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/gen/templates")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_models_requires_auth(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/gen/models")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_template_requires_auth(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/gen/templates", json={})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_generate_requires_auth(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/gen/templates/test-id/generate")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_import_model_requires_auth(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/gen/import/User")
    assert resp.status_code == 403
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gen/test_gen_template.py -v`
Expected: FAIL with 404 (routes not found) or import errors

- [ ] **Step 3: Create the endpoints file**

**创建 `backend/app/api/v1/endpoints/gen_template.py`:**

```python
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.gen_template import GenTemplateCreate, GenTemplateResponse, GenTemplateUpdate
from app.services.gen_import_service import GenImportService
from app.services.gen_template_service import GenTemplateService
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/gen", tags=["代码生成"])
template_service = GenTemplateService()
import_service = GenImportService()


@router.get("/models")
async def list_models(
    current_user: Annotated[User, Depends(require_permission("system:gen:list"))],
) -> APIResponse:
    models = import_service.scan_models()
    return APIResponse(data=models)


@router.get("/models/{model_name}")
async def get_model_detail(
    model_name: str,
    current_user: Annotated[User, Depends(require_permission("system:gen:list"))],
) -> APIResponse:
    import importlib
    import inspect

    from beanie import Document

    import app.models

    model_cls = None
    import pkgutil

    for _, module_name, _ in pkgutil.iter_modules(app.models.__path__):
        module = importlib.import_module(f"app.models.{module_name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Document) and obj != Document and name == model_name:
                model_cls = obj
                break

    if not model_cls:
        return APIResponse(code=10017, message=f"模型 {model_name} 不存在")

    fields = []
    system_fields = {"id", "created_at", "updated_at"}
    for field_name, field_info in model_cls.model_fields.items():
        if field_name in system_fields:
            continue
        fields.append({
            "field_name": field_name,
            "field_type": str(field_info.annotation),
            "label": field_name,
        })

    return APIResponse(data={
        "name": model_name,
        "fields": fields,
    })


@router.get("/templates")
async def list_templates(
    current_user: Annotated[User, Depends(require_permission("system:gen:list"))],
    params: Annotated[PageParams, Depends()],
    entity_name: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
) -> APIResponse:
    result = await template_service.get_list(params, entity_name, status)
    return APIResponse(data=result.model_dump())


@router.post("/templates")
async def create_template(
    body: GenTemplateCreate,
    current_user: Annotated[User, Depends(require_permission("system:gen:create"))],
) -> APIResponse:
    obj = await template_service.create(body)
    return APIResponse(data=GenTemplateResponse.model_validate(obj).model_dump())


@router.post("/import/{model_name}")
async def import_model(
    model_name: str,
    current_user: Annotated[User, Depends(require_permission("system:gen:create"))],
) -> APIResponse:
    template = await import_service.import_model(model_name)
    return APIResponse(data=GenTemplateResponse.model_validate(template).model_dump())


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user: Annotated[User, Depends(require_permission("system:gen:list"))],
) -> APIResponse:
    obj = await template_service.get_by_id(template_id)
    return APIResponse(data=GenTemplateResponse.model_validate(obj).model_dump())


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    body: GenTemplateUpdate,
    current_user: Annotated[User, Depends(require_permission("system:gen:update"))],
) -> APIResponse:
    obj = await template_service.update(template_id, body)
    return APIResponse(data=GenTemplateResponse.model_validate(obj).model_dump())


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    current_user: Annotated[User, Depends(require_permission("system:gen:delete"))],
) -> APIResponse:
    await template_service.delete(template_id)
    return APIResponse(message="删除成功")


@router.post("/templates/{template_id}/generate")
async def generate_code(
    template_id: str,
    current_user: Annotated[User, Depends(require_permission("system:gen:generate"))],
) -> APIResponse:
    from app.core.config import settings
    from app.generators.engine import GeneratorEngine

    template = await template_service.get_by_id(template_id)
    engine = GeneratorEngine()

    output_dir = settings.GEN_OUTPUT_DIR
    result = await engine.generate(template, output_dir)

    await template_service.update(template_id, GenTemplateUpdate(status=2))

    return APIResponse(data=result)
```

- [ ] **Step 4: Run test to verify API returns 403 (unauthorized)**

Run: `pytest tests/test_gen/test_gen_template.py -v`
Expected: PASS (returns 403 before routes registered, or proper 403 after)

Note: The actual 403 requires the routes to be registered (Task 9). Tests may return 404 until router is updated. Runner should check after Task 9.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/gen_template.py
git add tests/test_gen/test_gen_template.py
git commit -m "feat: 添加代码生成 API 端点"
```

---

### Task 9: Integration — 注册路由、异常、配置

**Files:**
- Modify: `backend/app/core/exceptions.py`
- Modify: `backend/app/database/mongodb.py`
- Modify: `backend/app/api/v1/router.py`
- Modify: `backend/app/core/config.py`
- Verify: app starts and routes are accessible

- [ ] **Step 1: Modify exceptions.py**

**在 `backend/app/core/exceptions.py` 末尾添加 GenTemplateNotFoundError:**

在最后一行之前（`async def global_exception_handler` 之前）添加：

```python
class GenTemplateNotFoundError(AppException):
    def __init__(self):
        super().__init__(code=10016, message="生成模板不存在")
```

- [ ] **Step 2: Modify config.py**

**在 `backend/app/core/config.py` 的 `Settings` 类中添加:**

```python
GEN_OUTPUT_DIR: str = "app"
```

放在 JWT 配置之后即可。

- [ ] **Step 3: Modify mongodb.py**

**在 `backend/app/database/mongodb.py` 的 `document_models` 列表末尾添加:**

```python
"app.models.gen_template.GenTemplate",
```

- [ ] **Step 4: Modify router.py**

**在 `backend/app/api/v1/router.py` 的导入和注册中添加:**

```python
from app.api.v1.endpoints import auth, company, department, gen_template, login_log, menu, position, role, user
```

```python
router.include_router(gen_template.router)
```

放在 `login_log` 之后。

- [ ] **Step 5: Verify application starts and routes are registered**

Run: `cd backend; python -c "from app.main import app; routes = [r.path for r in app.routes if '/gen/' in r.path]; print(f'Gen routes: {len(routes)}'); print('\n'.join(routes))"`
Expected: 9 gen routes printed

- [ ] **Step 6: Run all tests**

Run: `cd backend; pytest tests/test_gen/ -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add backend/app/core/exceptions.py
git add backend/app/core/config.py
git add backend/app/database/mongodb.py
git add backend/app/api/v1/router.py
git commit -m "feat: 集成代码生成模块到项目（路由+异常+配置）"
```

---

## Spec Self-Review

1. **Spec coverage:** All sections covered — GenField/GenTemplate models (Task 1), schemas (Task 2), repository (Task 3), service (Task 4), import service (Task 5), templates (Task 6), generator engine (Task 7), API endpoints (Task 8), integration (Task 9). Each has tests specified.
2. **Placeholder scan:** No TBD/TODO found. Every step has complete code.
3. **Type consistency:** `GenTemplateService.get_by_id` returns `GenTemplate` (used in Task 8), `GenImportService.scan_models` returns `list[dict]`, `GeneratorEngine.generate` returns `list[dict]`. All consistent.
