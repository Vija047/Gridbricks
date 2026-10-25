from fastapi import APIRouter

from app.api.routes import accuracy, actuals, forecasts, health, metadata

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(metadata.router)
api_router.include_router(forecasts.router)
api_router.include_router(actuals.router)
api_router.include_router(accuracy.router)
