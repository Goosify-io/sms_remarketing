from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client
from ..middleware import get_current_client

router = APIRouter()


class CreditBalance(BaseModel):
    credits: int


class AddCreditsRequest(BaseModel):
    amount: int


@router.get("/balance", response_model=CreditBalance)
def get_credit_balance(client: Client = Depends(get_current_client)):
    """Get current credit balance"""
    return CreditBalance(credits=client.credits)


@router.post("/add", response_model=CreditBalance)
def add_credits(
    request: AddCreditsRequest,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """
    Add credits to client account.
    Note: In production, this should be protected and integrated with a payment system.
    """
    client.credits += request.amount
    db.commit()
    db.refresh(client)
    return CreditBalance(credits=client.credits)
