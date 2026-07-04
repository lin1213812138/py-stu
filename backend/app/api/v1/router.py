from fastapi import APIRouter

from app.api.v1.endpoints import auth, company, department, login_log, menu, position, role, user

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(login_log.router)
router.include_router(user.router)
router.include_router(company.router)
router.include_router(department.router)
router.include_router(position.router)
router.include_router(menu.router)
router.include_router(role.router)
