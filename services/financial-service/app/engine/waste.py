from sqlmodel import Session, select
from app.models import Transaction
from app.schemas import InsightResponse
from typing import List
from datetime import datetime

def detect_waste(session: Session) -> List[InsightResponse]:
    insights = []
    # Example: Late-night Swiggy orders (after 11 PM)
    transactions = session.exec(select(Transaction)).all()
    late_night_total = 0
    late_night_count = 0
    
    for tx in transactions:
        if "swiggy" in tx.description.lower() and tx.date.hour >= 23:
            late_night_total += tx.amount
            late_night_count += 1
            
    if late_night_total > 500: # Arbitrary threshold for "waste"
        # score = (impact * 0.5) + (frequency * 0.3) + (recency * 0.2)
        score = (late_night_total * 0.5) + (late_night_count * 0.3) + (1 * 0.2)
        
        insights.append(InsightResponse(
            title="Late-night food spending is high",
            description=f"You spent ₹{late_night_total:.2f} extra this week on Swiggy after 11 PM.",
            confidence=0.85,
            impact=late_night_total,
            score=score,
            actions=["Set ₹200/day limit", "Disable late-night orders"],
            dynamic_prompts=["Show all late-night orders", "Set Swiggy budget"],
            state="ready"
        ))
    return insights
