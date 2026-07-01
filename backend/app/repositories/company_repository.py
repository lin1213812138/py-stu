import time
from typing import Optional
from app.models.company import Company
from app.utils.pagination import PageParams, PageResult


class CompanyRepository:

    @staticmethod
    async def create(company: Company) -> Company:
        return await company.insert()

    @staticmethod
    async def get_by_id(company_id: str) -> Optional[Company]:
        return await Company.get(company_id)

    @staticmethod
    async def get_by_name(name: str) -> Optional[Company]:
        return await Company.find_one(Company.name == name)

    @staticmethod
    async def get_list(params: PageParams, name: Optional[str] = None) -> PageResult:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        total = await Company.find(query).count()
        items = await Company.find(query).skip((params.page - 1) * params.page_size).limit(params.page_size).to_list()
        return PageResult(items=items, total=total, page=params.page, page_size=params.page_size, total_pages=(total + params.page_size - 1) // params.page_size)

    @staticmethod
    async def get_all() -> list[Company]:
        return await Company.find({"status": 1}).sort("sort").to_list()

    @staticmethod
    async def update(company_id: str, update_data: dict) -> Optional[Company]:
        company = await Company.get(company_id)
        if not company:
            return None
        update_data["updated_at"] = int(time.time())
        await company.update({"$set": update_data})
        return await Company.get(company_id)

    @staticmethod
    async def delete(company_id: str) -> bool:
        company = await Company.get(company_id)
        if not company:
            return False
        await company.delete()
        return True
