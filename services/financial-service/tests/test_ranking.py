from pydantic import BaseModel
from typing import List, Optional

class InsightResponse(BaseModel):
    title: str
    description: str
    impact: float
    score: float
    actions: List[str]
    dynamic_prompts: List[str]

def rank_insights(insights: List[InsightResponse]) -> InsightResponse:
    if not insights:
        return None
    sorted_insights = sorted(insights, key=lambda x: x.score, reverse=True)
    return sorted_insights[0]

# Mock Insights
i1 = InsightResponse(
    title="Overspending in Food",
    description="You spent ₹200 more than usual",
    impact=200,
    score=(200 * 0.5) + (1 * 0.3) + (1 * 0.2), # Impact 100.5
    actions=["Adjust limit"],
    dynamic_prompts=["Why did I overspend?"]
)

i2 = InsightResponse(
    title="Late-night Swiggy Waste",
    description="You spent ₹1200 on late-night orders",
    impact=1200,
    score=(1200 * 0.5) + (5 * 0.3) + (1 * 0.2), # Impact 601.7
    actions=["Set limit"],
    dynamic_prompts=["Show orders"]
)

top = rank_insights([i1, i2])
print(f"Top Insight: {top.title}")
print(f"Description: {top.description}")
print(f"Score: {top.score}")

assert top.title == "Late-night Swiggy Waste"
print("✅ Ranking Logic Verified!")
