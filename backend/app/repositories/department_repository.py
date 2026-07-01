from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.department import Department


class DepartmentRepository:

    @staticmethod
    async def create(dept: Department) -> Department:
        return await dept.insert()

    @staticmethod
    async def get_by_id(dept_id: UUID) -> Optional[Department]:
        return await Department.get(dept_id)

    @staticmethod
    async def get_by_company(company_id: UUID) -> list[Department]:
        return await Department.find({"company_id": company_id, "status": 1}).sort("sort").to_list()

    @staticmethod
    async def get_children(parent_id: UUID) -> list[Department]:
        return await Department.find({"parent_id": parent_id, "status": 1}).sort("sort").to_list()

    @staticmethod
    async def count_by_company(company_id: UUID) -> int:
        return await Department.find({"company_id": company_id}).count()

    @staticmethod
    async def update(dept_id: UUID, update_data: dict) -> Optional[Department]:
        dept = await Department.get(dept_id)
        if not dept:
            return None
        update_data["updated_at"] = datetime.utcnow()
        await dept.update({"$set": update_data})
        return await Department.get(dept_id)

    @staticmethod
    async def delete(dept_id: UUID) -> bool:
        dept = await Department.get(dept_id)
        if not dept:
            return False
        await dept.delete()
        return True
