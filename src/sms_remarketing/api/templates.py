from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Client, Template
from ..schemas import TemplateCreate, TemplateResponse, TemplateUpdate
from ..middleware import get_current_client

router = APIRouter()


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: TemplateCreate,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Create a new SMS template"""
    template = Template(**template_data.model_dump(), client_id=client.id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/", response_model=List[TemplateResponse])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """List all templates for the authenticated client"""
    query = db.query(Template).filter(Template.client_id == client.id)

    if active_only:
        query = query.filter(Template.is_active == True)

    templates = query.offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Get a specific template"""
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.client_id == client.id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Update a template"""
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.client_id == client.id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Update fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Delete a template"""
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.client_id == client.id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    db.delete(template)
    db.commit()
