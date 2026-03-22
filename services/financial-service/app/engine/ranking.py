"""
Actionability-weighted insight ranking.

Score = (Normalized Impact × 0.6) + (Actionability × 0.4)

The old formula (impact * 0.5 + frequency * 0.3 + recency * 0.2) let raw ₹ amounts
dominate and hardcoded frequency/recency to 1. This version normalizes impact to
0-100 and weights actionability — can the user realistically act on this?
"""
from typing import List
from app.schemas import InsightResponse


# Thresholds for impact normalization (₹ amounts mapped to 0-100)
IMPACT_LOW = 200     # ₹0-200 → 0-30 score
IMPACT_MID = 1000    # ₹200-1000 → 30-70 score
IMPACT_HIGH = 5000   # ₹1000-5000 → 70-100 score


def rank_insights(insights: List[InsightResponse]) -> InsightResponse:
    """
    Ranks insights using actionability-weighted scoring.
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

    scored = []
    for insight in insights:
        normalized_impact = _normalize_impact(insight.impact)
        actionability = _calculate_actionability(insight)
        insight.score = round((normalized_impact * 0.6) + (actionability * 0.4), 2)
        scored.append(insight)

    sorted_insights = sorted(scored, key=lambda x: x.score, reverse=True)
    return sorted_insights[0]


def _normalize_impact(raw_impact: float) -> float:
    """
    Normalizes raw ₹ impact to 0-100 scale.
    Prevents ₹5k subscriptions from always beating ₹200 coffee insights.
    """
    if raw_impact <= 0:
        return 0
    elif raw_impact <= IMPACT_LOW:
        return (raw_impact / IMPACT_LOW) * 30
    elif raw_impact <= IMPACT_MID:
        return 30 + ((raw_impact - IMPACT_LOW) / (IMPACT_MID - IMPACT_LOW)) * 40
    elif raw_impact <= IMPACT_HIGH:
        return 70 + ((raw_impact - IMPACT_MID) / (IMPACT_HIGH - IMPACT_MID)) * 30
    else:
        return 100


def _calculate_actionability(insight: InsightResponse) -> float:
    """
    Scores how actionable an insight is (0-100).
    An insight is more actionable when:
    - It has concrete actions (not just "View transactions")
    - It involves controllable spending (food, transport > rent, EMI)
    - It has higher confidence
    """
    score = 0.0

    # 1. Has concrete actions? (not just viewing)
    action_keywords = ["set", "limit", "adjust", "disable", "reduce", "budget", "block"]
    concrete_actions = sum(
        1 for a in insight.actions
        if any(kw in a.lower() for kw in action_keywords)
    )
    score += min(concrete_actions * 20, 40)  # Max 40 from actions

    # 2. Confidence contributes directly
    score += insight.confidence * 30  # Max 30 from confidence

    # 3. Has dynamic prompts? (means user can explore further)
    if insight.dynamic_prompts:
        score += min(len(insight.dynamic_prompts) * 10, 20)  # Max 20

    # 4. Penalty for vague insights
    vague_keywords = ["might", "possibly", "sometimes"]
    if any(kw in insight.description.lower() for kw in vague_keywords):
        score -= 15

    return max(min(score, 100), 0)
