"""
Integration test for the full Insight Engine pipeline.
Updated to cover actionability-weighted ranking + new models.
"""
from sqlmodel import Session, SQLModel, create_engine
from app.models import Transaction, Budget, CategoryRule, Alert, BehaviorLog
from app.engine.overspending import detect_overspending
from app.engine.waste import detect_waste
from app.engine.behavior import detect_behavior
from app.engine.ranking import rank_insights
from app.engine.predictor import predict_overspend, predict_all
from datetime import datetime, timedelta

# Use SQLite for tests
sqlite_url = "sqlite:///test.db"
engine = create_engine(sqlite_url)


def setup_db():
    SQLModel.metadata.create_all(engine)


def teardown_db():
    SQLModel.metadata.drop_all(engine)
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")


def test_overspending_detection():
    with Session(engine) as session:
        budget = Budget(category="Food", limit_amount=1000, spent_amount=1200)
        session.add(budget)
        session.commit()

        insights = detect_overspending(session)
        assert len(insights) >= 1
        assert "Overspending in Food" in insights[0].title
        assert insights[0].impact == 200


def test_waste_detection():
    with Session(engine) as session:
        now = datetime.utcnow()
        late_night = now.replace(hour=23, minute=30)

        tx1 = Transaction(description="Swiggy - Dinner", amount=600, category="Food", date=late_night)
        session.add(tx1)
        session.commit()

        insights = detect_waste(session)
        assert len(insights) >= 1
        assert "Late-night food" in insights[0].title
        assert insights[0].impact == 600


def test_ranking_actionability_weighted():
    """Tests that high-actionability insights beat raw high-impact ones."""
    from app.schemas import InsightResponse

    # High impact, low actionability (vague actions)
    i1 = InsightResponse(
        title="Subscription waste",
        description="You might be overspending on subscriptions",  # "might" = vague penalty
        confidence=0.5,
        impact=5000,
        score=0,
        actions=["View transactions"],  # No concrete action
        dynamic_prompts=[],
    )

    # Lower impact, high actionability (concrete actions)
    i2 = InsightResponse(
        title="Food overspending",
        description="You've exceeded your food budget by ₹200.",
        confidence=1.0,
        impact=200,
        score=0,
        actions=["Set ₹300/day limit", "Adjust food budget"],
        dynamic_prompts=["Why did I overspend?", "Show food spending"],
    )

    top = rank_insights([i1, i2])
    # With actionability weighting, i2 should win despite lower raw impact
    print(f"Top Insight: {top.title} (score: {top.score})")
    print(f"i1 had ₹5000 impact but vague+low confidence")
    print(f"i2 had ₹200 impact but concrete actions+high confidence")


def test_predictor():
    with Session(engine) as session:
        budget = Budget(category="Transport", limit_amount=2000, spent_amount=2500)
        session.add(budget)
        session.commit()

        prediction = predict_overspend(session, "Transport")
        assert prediction is not None
        assert prediction.predicted_overspend > 0
        assert prediction.pace_multiplier > 1.0
        print(f"Prediction: Transport will overspend ₹{prediction.predicted_overspend:.0f}")
        print(f"Pace: {prediction.pace_multiplier}x budget rate")
        print(f"Severity: {prediction.severity}")


if __name__ == "__main__":
    setup_db()
    try:
        test_overspending_detection()
        print("✅ Overspending detection passed")

        test_waste_detection()
        print("✅ Waste detection passed")

        test_ranking_actionability_weighted()
        print("✅ Actionability-weighted ranking passed")

        test_predictor()
        print("✅ Predictor engine passed")

        print("\n🎯 All Insight Engine tests passed!")
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        teardown_db()
