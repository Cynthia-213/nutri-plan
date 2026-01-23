from fastapi import APIRouter

from app.api.endpoints import users, foods, tracking, recommendations, exercises, blogs, rankings, notifications, body_metrics, performance, periodized_nutrition

# The main API router
api_router = APIRouter()

# Include the routers from the different modules
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(foods.router, prefix="/foods", tags=["Foods"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["Blogs"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["Rankings"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(body_metrics.router, prefix="/body-metrics", tags=["Body Metrics"])
api_router.include_router(performance.router, prefix="/performance", tags=["Performance Analysis"])
api_router.include_router(periodized_nutrition.router, prefix="/periodized-nutrition", tags=["Periodized Nutrition"])