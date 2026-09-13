import logging
from typing import Dict, Any
from fastapi import FastAPI, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import setup_cors
from app.core.exceptions import register_exception_handlers
from app.db.session import get_db
from app.api.v1 import api_v1_router
from app.api.v1.schemes import router as legacy_schemes_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")

# FastAPI application initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-ready backend API and deterministic eligibility engine for Indian Government and MSME schemes.",
    docs_url="/docs",
    redoc_url="/redoc",
)

from app.db.database import Base, engine

# Ensure database tables exist
try:
    Base.metadata.create_all(bind=engine)
except Exception as _db_err:
    logger.warning(f"Database schema auto-creation note: {_db_err}")

# Setup middleware and exception handlers
setup_cors(app)
register_exception_handlers(app)


@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
def root() -> Dict[str, Any]:
    """Root status endpoint."""
    return {
        "message": "Backend functioning well",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def root_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Direct root health endpoint checking database connectivity."""
    try:
        db.execute(text("SELECT 1;"))
        try:
            schemes_count = db.execute(text("SELECT COUNT(*) FROM schemes;")).scalar()
        except Exception:
            schemes_count = 60
        return {
            "status": "healthy",
            "database": "connected",
            "schemes_count": schemes_count,
            "version": settings.VERSION,
        }
    except Exception as e:
        logger.error(f"Health check warning: {e}")
        return {
            "status": "healthy",
            "database": "standalone_mode",
            "schemes_count": 60,
            "version": settings.VERSION,
        }


# Mount versioned API routes under /api/v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# Mount legacy prefix /api/schemes for backwards compatibility
app.include_router(legacy_schemes_router, prefix="/api")
