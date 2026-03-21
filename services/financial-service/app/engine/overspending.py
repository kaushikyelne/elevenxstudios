from sqlmodel import Session, select
from app.models import Transaction, Budget
from app.schemas import InsightResponse
from typing import List, Optional

def detect_overspending(session: Session) -> List[InsightResponse]:
    insights = []
    budgets = session.exec(select(Budget)).all()
    for b in budgets:
        if b.spent_amount > b.limit_amount:
            diff = b.spent_amount - b.limit_amount
            # score = (money_impact * 0.5) + (frequency * 0.3) + (recency * 0.2)
            # For overspending, frequency is 1 (current budget period), recency is high (current)
            score = (diff * 0.5) + (1 * 0.3) + (1 * 0.2)
            
            insights.append(InsightResponse(
                title=f"Overspending in {b.category}",
                description=f"You've exceeded your {b.category} budget by ₹{diff:.2f}.",
                confidence=1.0,
                impact=diff,
                score=score,
                actions=[f"Adjust {b.category} limit", "View transactions"],
                dynamic_prompts=[f"Why did I overspend in {b.category}?", f"Show {b.category} spending"],
                state="ready"
            ))
    return insights
