from fastapi import APIRouter

from app.api.endpoints import users, foods, tracking, recommendations, exercises

# The main API router
api_router = APIRouter()

# Include the routers from the different modules
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(foods.router, prefix="/foods", tags=["Foods"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
