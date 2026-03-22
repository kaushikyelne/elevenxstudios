"""
Tests for the overspend predictor.
Uses SQLite in-memory for isolation.
"""
import pytest
from datetime import datetime
from sqlmodel import Session, SQLModel, create_engine
from app.models import Budget
from app.engine.predictor import predict_overspend, predict_all, _calculate_severity
from app.engine.ranking import _normalize_impact
from app.schemas import InterventionSeverity


# In-memory SQLite for test isolation
engine = create_engine("sqlite://", echo=False)


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def _seed_budget(session, category="Food", limit=3000, spent=0, daily_limit=None):
    budget = Budget(
        category=category,
        limit_amount=limit,
        spent_amount=spent,
        daily_limit=daily_limit,
        month=datetime.utcnow().month,
        year=datetime.utcnow().year,
    )
    session.add(budget)
    session.commit()
    return budget


class TestPredictOverspend:
    def test_no_budget_returns_none(self):
        with Session(engine) as session:
            result = predict_overspend(session, "NonExistent")
            assert result is None

    def test_zero_limit_returns_none(self):
        with Session(engine) as session:
            _seed_budget(session, limit=0)
            result = predict_overspend(session, "Food")
            assert result is None

    def test_within_budget_no_overspend(self):
        with Session(engine) as session:
            # Day X of month, spent less than proportional budget
            _seed_budget(session, limit=3000, spent=100)
            result = predict_overspend(session, "Food")
            assert result is not None
            assert result.category == "Food"
            assert result.current_spent == 100

    def test_over_budget_produces_prediction(self):
        with Session(engine) as session:
            # Already spent more than limit
            _seed_budget(session, limit=1000, spent=1200)
            result = predict_overspend(session, "Food")
            assert result is not None
            assert result.predicted_overspend > 0
            assert result.pace_multiplier > 1.0

    def test_high_spending_critical_severity(self):
        with Session(engine) as session:
            _seed_budget(session, limit=1000, spent=1500)
            result = predict_overspend(session, "Food")
            assert result is not None
            assert result.severity == InterventionSeverity.CRITICAL

    def test_predict_all_multiple_categories(self):
        with Session(engine) as session:
            _seed_budget(session, category="Food", limit=1000, spent=1200)
            _seed_budget(session, category="Transport", limit=500, spent=600)
            results = predict_all(session)
            assert len(results) >= 2
            categories = [r.category for r in results]
            assert "Food" in categories
            assert "Transport" in categories


class TestSeverityCalculation:
    def test_low_severity(self):
        assert _calculate_severity(5, 40) == InterventionSeverity.LOW

    def test_medium_severity(self):
        assert _calculate_severity(15, 65) == InterventionSeverity.MEDIUM

    def test_high_severity(self):
        assert _calculate_severity(30, 90) == InterventionSeverity.HIGH

    def test_critical_severity_over_budget(self):
        assert _calculate_severity(10, 110) == InterventionSeverity.CRITICAL

    def test_critical_severity_high_overspend(self):
        assert _calculate_severity(60, 80) == InterventionSeverity.CRITICAL
