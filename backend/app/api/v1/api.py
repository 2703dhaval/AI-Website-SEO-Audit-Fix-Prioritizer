from fastapi import APIRouter

from app.api.v1.audits import router as audits_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.issues import router as issues_router
from app.api.v1.pages import router as pages_router
from app.api.v1.reports import router as reports_router
from app.api.v1.sample import router as sample_router

api_router = APIRouter()

api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(sample_router, prefix="/sample", tags=["sample"])
api_router.include_router(audits_router, prefix="/audits", tags=["audits"])
api_router.include_router(pages_router, prefix="/audits", tags=["pages"])
api_router.include_router(issues_router, prefix="/audits", tags=["issues"])
api_router.include_router(reports_router, prefix="/audits", tags=["reports"])
