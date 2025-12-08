from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Client, Lead
from ..schemas import LeadCreate, LeadResponse, LeadUpdate
from ..middleware import get_current_client

router = APIRouter()


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_data: LeadCreate,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Create a new lead and trigger NEW_LEAD automation"""
    lead = Lead(**lead_data.model_dump(), client_id=client.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)


    return lead


@router.get("/", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """List all leads for the authenticated client"""
    leads = (
        db.query(Lead)
        .filter(Lead.client_id == client.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Get a specific lead"""
    lead = (
        db.query(Lead).filter(Lead.id == lead_id, Lead.client_id == client.id).first()
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Update a lead"""
    lead = (
        db.query(Lead).filter(Lead.id == lead_id, Lead.client_id == client.id).first()
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Update fields
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Delete a lead"""
    lead = (
        db.query(Lead).filter(Lead.id == lead_id, Lead.client_id == client.id).first()
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    db.delete(lead)
    db.commit()
