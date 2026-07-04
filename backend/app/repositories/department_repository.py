import time
from typing import Optional

from app.models.department import Department


class DepartmentRepository:

    @staticmethod
    async def create(dept: Department) -> Department:
        return await dept.insert()

    @staticmethod
    async def get_by_id(dept_id: str) -> Optional[Department]:
        return await Department.get(dept_id)

    @staticmethod
    async def get_by_company(company_id: str) -> list[Department]:
        return await Department.find({"company_id": company_id, "status": 1}).sort("sort").to_list()

    @staticmethod
    async def get_children(parent_id: str) -> list[Department]:
        return await Department.find({"parent_id": parent_id, "status": 1}).sort("sort").to_list()

    @staticmethod
    async def count_by_company(company_id: str) -> int:
        return await Department.find({"company_id": company_id}).count()

    @staticmethod
    async def update(dept_id: str, update_data: dict) -> Optional[Department]:
        dept = await Department.get(dept_id)
        if not dept:
            return None
        update_data["updated_at"] = time.time() * 1000
        await dept.update({"$set": update_data})
        return await Department.get(dept_id)

    @staticmethod
    async def delete(dept_id: str) -> bool:
        dept = await Department.get(dept_id)
        if not dept:
            return False
        await dept.delete()
        return True
