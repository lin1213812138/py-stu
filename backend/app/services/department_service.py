from app.core.exceptions import AppException
from app.models.company import Company
from app.models.department import Department
from app.repositories.company_repository import CompanyRepository
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate


class DepartmentService:

    def __init__(self):
        self.repo = DepartmentRepository()

    async def get_tree(self, company_id: str) -> list[dict]:
        depts = await self.repo.get_by_company(company_id)
        dept_map = {str(d.id): DepartmentResponse.model_validate(d).model_dump() for d in depts}
        for d in depts:
            dept_map[str(d.id)]["children"] = []
        tree = []
        for d in depts:
            node = dept_map[str(d.id)]
            if d.parent_id and str(d.parent_id) in dept_map:
                dept_map[str(d.parent_id)]["children"].append(node)
            else:
                tree.append(node)
        return tree

    async def get_by_id(self, dept_id: str) -> Department:
        dept = await self.repo.get_by_id(dept_id)
        if not dept:
            raise AppException(code=10009, message="Department not found")
        return dept

    async def create(self, data: DepartmentCreate) -> Department:
        dept = Department(**data.model_dump())
        return await self.repo.create(dept)

    async def update(self, dept_id: str, data: DepartmentUpdate) -> Department:
        dept = await self.repo.update(dept_id, data.model_dump(exclude_unset=True))
        if not dept:
            raise AppException(code=10009, message="Department not found")
        return dept

    async def delete(self, dept_id: str) -> None:
        children = await self.repo.get_children(dept_id)
        if children:
            raise AppException(code=10013, message="Department has children, cannot delete")
        deleted = await self.repo.delete(dept_id)
        if not deleted:
            raise AppException(code=10009, message="Department not found")
