from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Client, Lead, Template, Message
from ..schemas import SendSMSRequest, MessageResponse
from ..middleware import get_current_client
from ..services import sms_service

router = APIRouter()


@router.post(
    "/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED
)
def send_sms(
    request: SendSMSRequest,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """
    Send an SMS to a lead.
    Either provide 'content' directly OR provide 'template_id' with optional 'variables'.
    """
    # Get lead
    lead = (
        db.query(Lead)
        .filter(Lead.id == request.lead_id, Lead.client_id == client.id)
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Determine content
    template = None
    if request.template_id:
        template = (
            db.query(Template)
            .filter(
                Template.id == request.template_id,
                Template.client_id == client.id,
                Template.is_active == True,
            )
            .first()
        )

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found or inactive",
            )

        # Render template with variables
        content = template.render(**request.variables)
    elif request.content:
        content = request.content
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'content' or 'template_id' must be provided",
        )

    # Send SMS
    try:
        message = sms_service.send_sms(
            db=db, client=client, lead=lead, content=content, template=template
        )
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[MessageResponse])
def list_messages(
    skip: int = 0,
    limit: int = 100,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """List all messages for the authenticated client"""
    messages = (
        db.query(Message)
        .filter(Message.client_id == client.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Get a specific message"""
    message = (
        db.query(Message)
        .filter(Message.id == message_id, Message.client_id == client.id)
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    return message
