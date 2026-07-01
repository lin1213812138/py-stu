"""
Initial seeder: create admin user, super admin role, and default menus.
Run: .venv\\Scripts\\python seed.py
"""
import asyncio

from app.core.config import settings
from app.core.security import hash_password
from app.database.mongodb import init_db
from app.models.company import Company
from app.models.department import Department
from app.models.menu import Menu
from app.models.role import Role, RolePermission
from app.models.user import User
from pymongo import AsyncMongoClient


ADMIN_MENUS = [
    {"type": "dir", "name": "系统管理", "path": "/system", "icon": "system", "sort": 1},
    {"type": "menu", "name": "用户管理", "path": "/system/user", "component": "system/user/index", "permission_key": "system:user:list", "parent_ref": "系统管理", "sort": 1},
    {"type": "menu", "name": "角色管理", "path": "/system/role", "component": "system/role/index", "permission_key": "system:role:list", "parent_ref": "系统管理", "sort": 2},
    {"type": "menu", "name": "菜单管理", "path": "/system/menu", "component": "system/menu/index", "permission_key": "system:menu:list", "parent_ref": "系统管理", "sort": 3},
    {"type": "menu", "name": "公司管理", "path": "/system/company", "component": "system/company/index", "permission_key": "system:company:list", "parent_ref": "系统管理", "sort": 4},
    {"type": "menu", "name": "部门管理", "path": "/system/dept", "component": "system/dept/index", "permission_key": "system:dept:list", "parent_ref": "系统管理", "sort": 5},
    {"type": "menu", "name": "岗位管理", "path": "/system/position", "component": "system/position/index", "permission_key": "system:position:list", "parent_ref": "系统管理", "sort": 6},
]

BUTTONS = {
    "用户管理": ["system:user:create", "system:user:update", "system:user:delete"],
    "角色管理": ["system:role:create", "system:role:update", "system:role:delete"],
    "菜单管理": ["system:menu:create", "system:menu:update", "system:menu:delete"],
    "公司管理": ["system:company:create", "system:company:update", "system:company:delete"],
    "部门管理": ["system:dept:create", "system:dept:update", "system:dept:delete"],
    "岗位管理": ["system:position:create", "system:position:update", "system:position:delete"],
}


async def seed():
    client = AsyncMongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    for coll in ["users", "roles", "menus", "companies", "departments", "positions"]:
        await db[coll].delete_many({})

    await init_db()

    company = await Company(name="默认公司", short_name="默认", sort=0).insert()
    dept = await Department(name="管理部", company_id=company.id, sort=0).insert()

    menu_map = {}
    for m in ADMIN_MENUS:
        parent_ref = m.pop("parent_ref", None)
        parent_id = menu_map.get(parent_ref) if parent_ref else None
        menu = await Menu(parent_id=parent_id, **m).insert()
        menu_map[m["name"]] = menu.id

    all_menu_ids = []
    button_refs = {}
    for menu_name, button_keys in BUTTONS.items():
        parent_id = menu_map[menu_name]
        all_menu_ids.append(parent_id)
        for key in button_keys:
            btn = await Menu(
                parent_id=parent_id,
                type="button",
                name=key,
                permission_key=key,
                sort=0,
            ).insert()
            button_refs.setdefault(menu_name, []).append(key)

    role = await Role(
        name="超级管理员",
        code="super_admin",
        permissions=[
            RolePermission(menu_id=mid, button_keys=BUTTONS.get(name, []))
            for mid, name in [
                (menu_map[n], n) for n in BUTTONS if n in menu_map
            ]
        ],
    ).insert()

    await User(
        username="admin",
        email="admin@admin.com",
        password_hash=hash_password("admin123"),
        nickname="管理员",
        role="admin",
        company_id=company.id,
        department_id=dept.id,
        role_ids=[role.id],
    ).insert()

    print("Seed complete! Admin account: admin / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
