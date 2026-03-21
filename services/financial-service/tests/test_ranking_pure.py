def rank_insights(insights):
    if not insights:
        return None
    # score = (money_impact * 0.5) + (frequency * 0.3) + (recency * 0.2)
    sorted_insights = sorted(insights, key=lambda x: x['score'], reverse=True)
    return sorted_insights[0]

# Mock Insights
i1 = {
    "title": "Overspending in Food",
    "score": (200 * 0.5) + (1 * 0.3) + (1 * 0.2) # ~100.5
}

i2 = {
    "title": "Late-night Swiggy Waste",
    "score": (1200 * 0.5) + (5 * 0.3) + (1 * 0.2) # ~601.7
}

top = rank_insights([i1, i2])
print(f"Top Insight: {top['title']}")
print(f"Score: {top['score']}")

assert top['title'] == "Late-night Swiggy Waste"
print("✅ Pure-Python Ranking Logic Verified!")
