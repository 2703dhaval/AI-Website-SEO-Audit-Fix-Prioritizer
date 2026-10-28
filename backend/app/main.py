import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.sample_report_data import seed_sample_company_audit

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("seo_audit_pro")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed sample report
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)

    # Pre-seed Scalezix sample report
    db = SessionLocal()
    try:
        seed_sample_company_audit(db)
        logger.info("Sample company audit verified/seeded successfully.")
    except Exception as e:
        logger.warning(f"Could not seed sample audit on startup: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down SEO Audit Pro...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade AI Website SEO Audit & Fix Prioritizer REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development ports and previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Safe error handling to prevent leaking internal stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc!s}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact support or check server logs."
        },
    )


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint verifying database connectivity."""
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e!s}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "1.0.0",
        "project": settings.PROJECT_NAME,
        "database": db_status,
        "environment": "production"
        if not settings.ALLOW_LOCAL_TEST_DOMAINS
        else "development",
    }


# Mount v1 REST API
app.include_router(api_router, prefix=settings.API_V1_STR)
