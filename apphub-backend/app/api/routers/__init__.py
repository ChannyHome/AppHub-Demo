from fastapi import APIRouter
from app.api.routers.health import router as health_router
from app.api.routers.auth import router as auth_router
from app.api.routers.jobs import router as jobs_router
from app.api.routers.apps import router as apps_router
from app.api.routers.access import router as access_router
from app.api.routers.notices import router as notices_router
from app.api.routers.hub_events import router as hub_events_router
from app.api.routers.app_events import router as app_events_router
from app.api.routers.app_events_admin import router as app_events_admin
from app.api.routers.metrics import router as metrics_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(jobs_router, tags=["jobs"])
api_router.include_router(apps_router, tags=["apps"])
api_router.include_router(access_router, tags=["access"])
api_router.include_router(notices_router, tags=["notices"])
api_router.include_router(hub_events_router, tags=["hub-events"])
api_router.include_router(app_events_router, tags=["app-events"])
api_router.include_router(app_events_admin, tags=["app-events-admin"])
api_router.include_router(metrics_router, tags=["metrics"])
