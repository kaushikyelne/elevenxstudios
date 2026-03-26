from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Budget
from app.schemas import BudgetStatus
from app.database import get_session
from typing import List

router = APIRouter()

def calculate_status_color(percentage: float) -> str:
    if percentage < 60:
        return "Green"
    elif percentage < 85:
        return "Yellow"
    return "Red"

@router.get("/", response_model=List[BudgetStatus])
async def get_budgets(session: Session = Depends(get_session)):
    budgets = session.exec(select(Budget)).all()
    results = []
    for b in budgets:
        percentage = (b.spent_amount / b.limit_amount * 100) if b.limit_amount > 0 else 0
        results.append(BudgetStatus(
            category=b.category,
            limit_amount=b.limit_amount,
            spent_amount=b.spent_amount,
            percentage_used=round(percentage, 2),
            status_color=calculate_status_color(percentage)
        ))
    return results

@router.post("/", response_model=Budget)
async def create_budget(budget: Budget, session: Session = Depends(get_session)):
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget
