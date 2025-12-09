from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Client, Trigger, Template
from ..schemas import TriggerCreate, TriggerResponse, TriggerUpdate
from ..middleware import get_current_client

router = APIRouter()


@router.post("/", response_model=TriggerResponse, status_code=status.HTTP_201_CREATED)
def create_trigger(
    trigger_data: TriggerCreate,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Create a new automation trigger"""
    # Verify template belongs to client
    template = (
        db.query(Template)
        .filter(
            Template.id == trigger_data.template_id, Template.client_id == client.id
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    trigger = Trigger(**trigger_data.model_dump(), client_id=client.id)
    db.add(trigger)
    db.commit()
    db.refresh(trigger)
    return trigger


@router.get("/", response_model=List[TriggerResponse])
def list_triggers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """List all triggers for the authenticated client"""
    query = db.query(Trigger).filter(Trigger.client_id == client.id)

    if active_only:
        query = query.filter(Trigger.is_active == True)

    triggers = query.offset(skip).limit(limit).all()
    return triggers


@router.get("/{trigger_id}", response_model=TriggerResponse)
def get_trigger(
    trigger_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Get a specific trigger"""
    trigger = (
        db.query(Trigger)
        .filter(Trigger.id == trigger_id, Trigger.client_id == client.id)
        .first()
    )

    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trigger not found"
        )

    return trigger


@router.put("/{trigger_id}", response_model=TriggerResponse)
def update_trigger(
    trigger_id: int,
    trigger_data: TriggerUpdate,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Update a trigger"""
    trigger = (
        db.query(Trigger)
        .filter(Trigger.id == trigger_id, Trigger.client_id == client.id)
        .first()
    )

    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trigger not found"
        )

    # Update fields
    update_data = trigger_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trigger, field, value)

    db.commit()
    db.refresh(trigger)
    return trigger


@router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trigger(
    trigger_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Delete a trigger"""
    trigger = (
        db.query(Trigger)
        .filter(Trigger.id == trigger_id, Trigger.client_id == client.id)
        .first()
    )

    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trigger not found"
        )

    db.delete(trigger)
    db.commit()
