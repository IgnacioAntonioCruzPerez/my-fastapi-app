"""API key authentication."""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

# Use APIKeyHeader so Swagger UI "Authorize" sends the header correctly
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(API_KEY_HEADER)):
    """Validate static API key from X-API-Key header."""
    if not api_key or api_key.strip() != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide X-API-Key header.",
        )
    return api_key
