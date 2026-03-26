from sqlmodel import Session, select
from app.models import Transaction
from app.schemas import InsightResponse
from typing import List

def detect_behavior(session: Session) -> List[InsightResponse]:
    insights = []
    # Example: Uber on weekdays after 9 PM
    transactions = session.exec(select(Transaction)).all()
    uber_late_count = 0
    
    for tx in transactions:
        if "uber" in tx.description.lower() and tx.date.weekday() < 5 and tx.date.hour >= 21:
            uber_late_count += 1
            
    if uber_late_count >= 3:
        # score = (impact * 0.5) + (frequency * 0.3) + (recency * 0.2)
        impact = uber_late_count * 200
        score = (impact * 0.5) + (uber_late_count * 0.3) + (1 * 0.2)
        
        insights.append(InsightResponse(
            title="Weekday Uber habit detected",
            description=f"You take Uber {uber_late_count}x more on weekdays after 9 PM.",
            confidence=0.75,
            impact=impact,
            score=score,
            actions=["Check public transport", "Setup ride-share alerts"],
            dynamic_prompts=["Why do I take Uber so late?", "Show late-night Ubers"],
            state="ready"
        ))
    return insights
