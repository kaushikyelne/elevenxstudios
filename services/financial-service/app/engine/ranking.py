from typing import List
from app.schemas import InsightResponse

def rank_insights(insights: List[InsightResponse]) -> InsightResponse:
    """
    Ranks insights based on score = (money_impact * 0.5) + (frequency * 0.3) + (recency * 0.2).
    Returns the top insight or a default no-data insight.
    """
    if not insights:
        return InsightResponse(
            title="Welcome to MoneyLane",
            description="Add some transactions to see your personalized insights.",
            confidence=1.0,
            impact=0,
            score=0,
            actions=["Add Transaction"],
            dynamic_prompts=["How to add transactions?", "Show my balance"],
            state="no_data"
        )
    
    # Insights are already scored by their respective engines
    sorted_insights = sorted(insights, key=lambda x: x.score, reverse=True)
    return sorted_insights[0]
