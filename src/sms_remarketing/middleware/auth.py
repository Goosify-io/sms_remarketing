from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


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
