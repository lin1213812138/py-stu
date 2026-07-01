from uuid import UUID

from app.core.exceptions import AppException
from app.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.utils.pagination import PageParams


class CompanyService:

    def __init__(self):
        self.repo = CompanyRepository()

    async def get_list(self, params: PageParams, name: str | None = None):
        return await self.repo.get_list(params, name)

    async def get_all(self) -> list[Company]:
        return await self.repo.get_all()

    async def get_by_id(self, company_id: UUID) -> Company:
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise AppException(code=10008, message="Company not found")
        return company

    async def create(self, data: CompanyCreate) -> Company:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise AppException(code=10015, message="Duplicate company name")
        company = Company(**data.model_dump())
        return await self.repo.create(company)

    async def update(self, company_id: UUID, data: CompanyUpdate) -> Company:
        company = await self.repo.update(company_id, data.model_dump(exclude_unset=True))
        if not company:
            raise AppException(code=10008, message="Company not found")
        return company

    async def delete(self, company_id: UUID) -> None:
        deleted = await self.repo.delete(company_id)
        if not deleted:
            raise AppException(code=10008, message="Company not found")
