from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Client
from ..schemas import ClientCreate, ClientResponse, ClientUpdate
from ..middleware.auth import verify_admin

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_admin),
):
    """
    Create a new client account.
    Returns the client with generated API key.
    Requires admin authentication via X-Admin-API-Key header.
    """
    # Check if email already exists
    existing = db.query(Client).filter(Client.email == client_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create client with generated API key
    client = Client(
        name=client_data.name,
        email=client_data.email,
        api_key=Client.generate_api_key(),
        credits=client_data.initial_credits,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_admin),
):
    """
    List all clients.
    Requires admin authentication via X-Admin-API-Key header.
    """
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int, db: Session = Depends(get_db), _admin: bool = Depends(verify_admin)
):
    """
    Get a specific client.
    Requires admin authentication via X-Admin-API-Key header.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_admin),
):
    """
    Update a client.
    Requires admin authentication via X-Admin-API-Key header.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int, db: Session = Depends(get_db), _admin: bool = Depends(verify_admin)
):
    """
    Delete a client.
    Requires admin authentication via X-Admin-API-Key header.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    db.delete(client)
    db.commit()
