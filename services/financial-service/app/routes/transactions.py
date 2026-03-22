"""
Transaction routes — now triggers the Intervention Engine on every write.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Transaction, CategoryRule, Budget
from app.schemas import InterventionResponse, TransactionCreateResponse, TransactionBase
from app.database import get_session
from app.engine.intervention import check_and_intervene
from typing import List
import logging

logger = logging.getLogger(__name__)

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


@router.post("/", response_model=TransactionCreateResponse)
async def create_transaction(body: TransactionBase, session: Session = Depends(get_session)):
    """
    Create a transaction, auto-update the budget, and trigger the intervention engine.
    Returns both the transaction AND any intervention that fired.
    """
    # Build Transaction model from validated schema (ensures datetime coercion)
    tx = Transaction(
        amount=body.amount,
        description=body.description,
        category=body.category,
        date=body.date,
        merchant=body.merchant,
    )

    # 1. Auto-categorize
    if not tx.manual_override:
        tx.category = categorize_transaction(tx.description, session)

    # 2. Save transaction
    session.add(tx)
    session.commit()
    session.refresh(tx)

    # 3. Auto-update budget spent_amount
    budget = session.exec(
        select(Budget).where(Budget.category == tx.category)
    ).first()
    if budget:
        budget.spent_amount += tx.amount
        session.add(budget)
        session.commit()
        session.refresh(budget)

    # 4. Trigger intervention engine
    intervention = InterventionResponse(triggered=False)
    try:
        intervention = await check_and_intervene(session, tx)
    except Exception as e:
        logger.error(f"Intervention engine error: {e}")

    return TransactionCreateResponse(
        transaction=TransactionBase.model_validate(tx),
        intervention=intervention,
    )
