from sqlmodel import Session, SQLModel, create_engine
from app.models import Transaction, Budget, CategoryRule
from app.engine.overspending import detect_overspending
from app.engine.waste import detect_waste
from app.engine.behavior import detect_behavior
from app.engine.ranking import rank_insights
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
        # Add a budget and exceeding transaction
        budget = Budget(category="Food", limit_amount=1000, spent_amount=1200)
        session.add(budget)
        session.commit()
        
        insights = detect_overspending(session)
        assert len(insights) >= 1
        assert "Overspending in Food" in insights[0].title
        assert insights[0].impact == 200

def test_waste_detection():
    with Session(engine) as session:
        # Add late-night swiggy transactions
        now = datetime.utcnow()
        late_night = now.replace(hour=23, minute=30)
        
        tx1 = Transaction(description="Swiggy - Dinner", amount=600, category="Food", date=late_night)
        session.add(tx1)
        session.commit()
        
        insights = detect_waste(session)
        assert len(insights) >= 1
        assert "Late-night food" in insights[0].title
        assert insights[0].impact == 600

def test_ranking_logic():
    from app.schemas import InsightResponse
    
    i1 = InsightResponse(title="Low impact", description="...", confidence=1, impact=100, score=10, actions=[], dynamic_prompts=[])
    i2 = InsightResponse(title="High impact", description="...", confidence=1, impact=1000, score=100, actions=[], dynamic_prompts=[])
    
    top = rank_insights([i1, i2])
    assert top.title == "High impact"

if __name__ == "__main__":
    setup_db()
    try:
        test_overspending_detection()
        test_waste_detection()
        test_ranking_logic()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        teardown_db()
