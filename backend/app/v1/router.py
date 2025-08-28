from fastapi import APIRouter

from app.v1.routes import roots, fields, models

api_v1_router = APIRouter()

api_v1_router.include_router(roots.router, prefix="/roots", tags=["roots"])
api_v1_router.include_router(fields.router, prefix="/fields", tags=["fields"])
api_v1_router.include_router(models.router, prefix="/models", tags=["models"]) 