"""FastAPI application: Organizations, Buildings, and Activities directory API."""
from fastapi import FastAPI

from app.api import organizations, buildings, activities
from app.config import settings

app = FastAPI(
    title="Directory API",
    description="REST API for Organizations, Buildings, and Activities directory. "
    "All endpoints require X-API-Key header. Activity tree is limited to 3 levels.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(organizations.router, prefix="/api")
app.include_router(buildings.router, prefix="/api")
app.include_router(activities.router, prefix="/api")


@app.get("/")
def root():
    """Health check and API info."""
    return {
        "message": "Directory API",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


@app.get("/health")
def health():
    """Health check for deployment."""
    return {"status": "ok"}


@app.get("/api-key-info")
def api_key_info():
    """
    Return the API key and header name for frontend use.
    Call this once (no auth) then send the key in X-API-Key header for all other requests.
    """
    return {
        "header_name": "X-API-Key",
        "api_key": settings.api_key,
    }
