from fastapi import APIRouter

from app.api import auth, houses, import_api, ml, stats

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(houses.router)
api_router.include_router(stats.router)
api_router.include_router(import_api.router)
api_router.include_router(ml.router)
