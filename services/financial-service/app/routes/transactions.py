from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Transaction, CategoryRule
from app.database import get_session
from typing import List

router = APIRouter()

def categorize_transaction(description: str, session: Session) -> str:
    """Simple rule-based categorization."""
    rules = session.exec(select(CategoryRule)).all()
    for rule in rules:
        if rule.keyword.lower() in description.lower():
            return rule.category
    return "Miscellaneous"

@router.get("/", response_model=List[Transaction])
async def get_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction)).all()

@router.post("/", response_model=Transaction)
async def create_transaction(tx: Transaction, session: Session = Depends(get_session)):
    if not tx.manual_override:
        tx.category = categorize_transaction(tx.description, session)
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx
