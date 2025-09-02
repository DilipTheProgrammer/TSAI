"""Main API router"""

from fastapi import APIRouter

from app.api.v1.endpoints import prediction, entities, search, cohort

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(cohort.router, prefix="/cohort", tags=["cohort"])
