from fastapi import APIRouter

from app.api.routes import mentions, monitoring, alerts, analytics, sentiment

router = APIRouter()

# Include all route modules
router.include_router(mentions.router, prefix="/mentions", tags=["mentions"])
router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])