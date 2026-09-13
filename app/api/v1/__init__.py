from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.schemes import router as schemes_router
from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.business_profiles import router as business_profiles_router
from app.api.v1.programs import router as programs_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.research import router as research_router
from app.api.v1.dpr import router as dpr_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(schemes_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(business_profiles_router)
api_v1_router.include_router(programs_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(research_router)
api_v1_router.include_router(dpr_router)

__all__ = ["api_v1_router"]

