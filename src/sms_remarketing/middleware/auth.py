from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client
from ..config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
admin_api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


async def get_current_client(
    api_key: str = Depends(api_key_header), db: Session = Depends(get_db)
) -> Client:
    """
    Authenticate client using API key from X-API-Key header.
    Returns the authenticated client or raises 401 error.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Provide it in X-API-Key header.",
        )

    client = db.query(Client).filter(Client.api_key == api_key).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Client account is inactive"
        )

    return client


async def verify_admin(admin_key: str = Depends(admin_api_key_header)) -> bool:
    """
    Authenticate admin using admin API key from X-Admin-API-Key header.
    Returns True if authenticated or raises 401/403 error.
    """
    if not admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API key is missing. Provide it in X-Admin-API-Key header.",
        )

    if admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin API key"
        )

    return True
