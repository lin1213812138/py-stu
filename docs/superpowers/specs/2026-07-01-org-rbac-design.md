# Organizational Structure & RBAC — Design Spec

**Date:** 2026-07-01
**Project:** python-stu — Phase 2: Organization + Role-Based Access Control

---

## 1. Overview

Phase 2 extends the existing auth/user foundation with two subsystems:

| Subsystem | Modules | Description |
|-----------|---------|-------------|
| **A: Organizational Structure** | Company, Department, Position | Multi-company org hierarchy |
| **B: RBAC** | Menu, Role, Permission | Menu tree + dynamic permission assignment + button-level ACL |

## 2. Architecture

Follows existing strict layering: `Router → Service → Repository → ODM (Beanie)`

### New Files

```
app/
├── models/
│   ├── company.py
│   ├── department.py
│   ├── position.py
│   ├── menu.py
│   └── role.py
├── schemas/
│   ├── company.py
│   ├── department.py
│   ├── position.py
│   ├── menu.py
│   └── role.py
├── repositories/
│   ├── company_repository.py
│   ├── department_repository.py
│   ├── position_repository.py
│   ├── menu_repository.py
│   └── role_repository.py
├── services/
│   ├── company_service.py
│   ├── department_service.py
│   ├── position_service.py
│   ├── menu_service.py
│   ├── role_service.py
│   └── permission_service.py
├── api/v1/endpoints/
│   ├── company.py
│   ├── department.py
│   ├── position.py
│   ├── menu.py
│   └── role.py
└── tests/
    ├── test_company.py
    ├── test_department.py
    ├── test_position.py
    ├── test_menu.py
    └── test_role.py
```

### Modified Files

| File | Change |
|------|--------|
| `models/user.py` | Add `company_id`, `department_id`, `position_id`, `role_ids` |
| `api/deps.py` | Add `require_permission()`, deprecate `require_role()` |
| `api/v1/router.py` | Register new routers |
| `api/v1/endpoints/user.py` | Support new fields in create/update |
| `schemas/user.py` | Add new fields to schemas |

## 3. Data Models

### Entity Relationship

```
Company ──1:N── Department ──1:N── Position
  │                     │
  │ (redundant)         │ (1:1)
  ▼                     ▼
User ◄──N:N── Role ◄──N:N(embedded)── Menu ──1:N── Menu(buttons)

User.company_id    → 冗余，通过 department 反查
User.department_id → 一对一归属
User.position_id   → 一对一归属
User.role_ids[]    → 多对多角色
Role.permissions[] → 嵌入文档 [{menu_id, button_keys[]}]
```

### Company

```python
class Company(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str                                            # unique
    short_name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    status: int = 1                                      # 1=active 0=disabled
    sort: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "companies"
```

### Department

```python
class Department(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str
    company_id: UUID
    parent_id: Optional[UUID] = None                     # tree support
    leader_id: Optional[UUID] = None
    status: int = 1
    sort: int = 0
    created_at: datetime
    updated_at: datetime

    class Settings:
        name = "departments"
```

### Position

```python
class Position(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str
    department_id: UUID
    status: int = 1
    sort: int = 0
    created_at: datetime
    updated_at: datetime

    class Settings:
        name = "positions"
```

### Menu

```python
class Menu(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    parent_id: Optional[UUID] = None
    type: str                                            # "dir" | "menu" | "link" | "button"
    name: str                                            # display name
    permission_key: Optional[str] = None                 # required for button, optional for menu
    path: Optional[str] = None                           # route path (required for menu/link)
    component: Optional[str] = None                      # frontend component (required for menu)
    icon: Optional[str] = None
    sort: int = 0
    visible: int = 1                                     # 0=hidden 1=visible
    is_frame: int = 0                                    # 0=no 1=yes (external iframe)
    is_cache: int = 0                                    # 0=no-cache 1=cache (keep-alive)
    is_affix: int = 0                                    # 0=no 1=yes (pinned tab)
    query: Optional[str] = None                          # route params JSON
    remark: Optional[str] = None
    status: int = 1
    created_at: datetime
    updated_at: datetime

    class Settings:
        name = "menus"
```

| type | path | component | permission_key |
|------|------|-----------|----------------|
| dir | optional | none | none |
| menu | required | required | optional |
| link | required(URL) | none | none |
| button | none | none | required |

### Role

```python
class RolePermission(BaseModel):                         # embedded document
    menu_id: UUID
    button_keys: list[str] = []                          # enabled button permission_keys

class Role(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str
    code: str                                            # unique
    permissions: list[RolePermission] = []
    status: int = 1
    created_at: datetime
    updated_at: datetime

    class Settings:
        name = "roles"
```

### User (Modified)

New fields added to existing User Document:

```python
# Added to User:
company_id: Optional[UUID] = None          # redundant (derived from department)
department_id: Optional[UUID] = None       # 1:1
position_id: Optional[UUID] = None         # 1:1  
role_ids: list[UUID] = []                  # N:N
# Deprecated (kept for backward compat):
# role: str = "user"
```

## 4. API Endpoints

### Company

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/v1/companies` | - | List (paginated) |
| GET | `/api/v1/companies/all` | - | All (dropdown) |
| POST | `/api/v1/companies` | `system:company:create` | Create |
| GET | `/api/v1/companies/{id}` | - | Detail |
| PUT | `/api/v1/companies/{id}` | `system:company:update` | Update |
| DELETE | `/api/v1/companies/{id}` | `system:company:delete` | Delete |

### Department

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/v1/departments` | - | Tree (filter by company) |
| POST | `/api/v1/departments` | `system:dept:create` | Create |
| GET | `/api/v1/departments/{id}` | - | Detail |
| PUT | `/api/v1/departments/{id}` | `system:dept:update` | Update |
| DELETE | `/api/v1/departments/{id}` | `system:dept:delete` | Delete |

### Position

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/v1/positions` | - | List (filter by dept) |
| POST | `/api/v1/positions` | `system:position:create` | Create |
| GET | `/api/v1/positions/{id}` | - | Detail |
| PUT | `/api/v1/positions/{id}` | `system:position:update` | Update |
| DELETE | `/api/v1/positions/{id}` | `system:position:delete` | Delete |

### Menu

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/v1/menus` | - | Full menu tree |
| GET | `/api/v1/menus/user` | Bearer | User menu tree (by roles) |
| POST | `/api/v1/menus` | `system:menu:create` | Create |
| GET | `/api/v1/menus/{id}` | - | Detail |
| PUT | `/api/v1/menus/{id}` | `system:menu:update` | Update |
| DELETE | `/api/v1/menus/{id}` | `system:menu:delete` | Delete |

### Role

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/v1/roles` | - | List (paginated) |
| GET | `/api/v1/roles/all` | - | All (dropdown) |
| POST | `/api/v1/roles` | `system:role:create` | Create |
| GET | `/api/v1/roles/{id}` | - | Detail (with permissions) |
| PUT | `/api/v1/roles/{id}` | `system:role:update` | Update (with permission assignment) |
| DELETE | `/api/v1/roles/{id}` | `system:role:delete` | Delete |

### Role Permission Assignment

```json
// PUT /api/v1/roles/{id}
{
  "name": "运营经理",
  "code": "operation_manager",
  "status": 1,
  "permissions": [
    { "menu_id": "uuid-of-menu-page", "button_keys": ["system:user:create", "system:user:update"] },
    { "menu_id": "uuid-of-dept-page", "button_keys": [] }
  ]
}
```

**Default behavior:** When a menu page is assigned, all its child buttons are auto-included via `button_keys`. User can deselect individual buttons.

## 5. Permission System

### Permission Key Convention

```
system:<module>:<action>

Examples:
system:company:create / system:company:update / system:company:delete
system:dept:create / system:dept:update / system:dept:delete
system:position:create / system:position:update / system:position:delete
system:menu:create / system:menu:update / system:menu:delete
system:role:create / system:role:update / system:role:delete
system:user:create / system:user:update / system:user:delete
```

### Backend Permission Check

```python
# api/deps.py
async def require_permission(key: str):
    async def checker(current_user = Depends(get_current_user)):
        allowed = await PermissionService.get_user_permissions(current_user.role_ids)
        if key not in allowed:
            raise PermissionDeniedError()
        return current_user
    return checker

# Usage:
@router.delete("/{id}")
async def delete(..., current_user = Depends(require_permission("system:user:delete"))):
```

### Permission Aggregation Logic

```python
class PermissionService:
    @staticmethod
    async def get_user_permissions(role_ids: list[UUID]) -> set[str]:
        """Aggregate all permission_keys from user's roles."""
        keys = set()
        roles = await Role.find({"_id": {"$in": role_ids}, "status": 1}).to_list()
        for role in roles:
            for perm in role.permissions:
                menu = await Menu.get(perm.menu_id)
                if menu and menu.status == 1:
                    if menu.permission_key:
                        keys.add(menu.permission_key)
                    keys.update(perm.button_keys)
        return keys
```

### Dynamic User Menu Tree

```
GET /api/v1/menus/user
```

Returns menu tree filtered by user's role permissions: only menus whose `id` appears in any assigned role's `permissions[].menu_id`, with `type` in (`dir`, `menu`, `link`) and `visible=1`.

## 6. Error Codes (Extended)

| Code | Description |
|------|-------------|
| 10001 | General business error |
| 10002 | User already exists |
| 10003 | User not found |
| 10004 | Invalid credentials |
| 10005 | Token expired/invalid |
| 10006 | Insufficient permissions |
| 10007 | Validation error |
| 10008 | Company not found |
| 10009 | Department not found |
| 10010 | Position not found |
| 10011 | Menu not found |
| 10012 | Role not found |
| 10013 | Department has children, cannot delete |
| 10014 | Duplicate role code |
| 10015 | Duplicate company name |

## 7. Out of Scope

- Data permission (row-level ACL per company/dept)
- Operation logs / audit trail
- Bulk operations (batch delete, import/export)
- Org chart visualization
