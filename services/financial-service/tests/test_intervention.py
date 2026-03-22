"""
Tests for the Intervention Engine.
Uses SQLite in-memory for isolation.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine
from app.models import Budget, Transaction, Alert
from app.engine.intervention import check_and_intervene, ALERT_COOLDOWN_HOURS
from app.schemas import InterventionSeverity


engine = create_engine("sqlite://", echo=False)


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def _make_tx(category="Food", amount=500, description="Swiggy order"):
    return Transaction(
        amount=amount,
        description=description,
        category=category,
        date=datetime.utcnow(),
    )


def _seed_budget(session, category="Food", limit=3000, spent=0, daily_limit=None, is_blocked=False):
    budget = Budget(
        category=category,
        limit_amount=limit,
        spent_amount=spent,
        daily_limit=daily_limit,
        is_blocked=is_blocked,
        month=datetime.utcnow().month,
        year=datetime.utcnow().year,
    )
    session.add(budget)
    session.commit()
    return budget


class TestIntervention:
    def test_no_budget_no_intervention(self):
        with Session(engine) as session:
            tx = _make_tx(category="Unknown")
            session.add(tx)
            session.commit()
            result = check_and_intervene(session, tx)
            assert result.triggered is False

    def test_soft_block_triggers_warning(self):
        with Session(engine) as session:
            _seed_budget(session, is_blocked=True, spent=100)
            tx = _make_tx()
            session.add(tx)
            session.commit()
            result = check_and_intervene(session, tx)
            assert result.triggered is True
            assert result.alert_type == "soft_block"
            assert result.severity == InterventionSeverity.HIGH
            assert len(result.suggested_actions) == 2

    def test_daily_limit_breach(self):
        with Session(engine) as session:
            _seed_budget(session, daily_limit=200, spent=100)
            # Create transactions for today totaling over 200
            tx1 = _make_tx(amount=150)
            tx2 = _make_tx(amount=100)
            session.add(tx1)
            session.add(tx2)
            session.commit()
            result = check_and_intervene(session, tx2)
            assert result.triggered is True
            assert result.alert_type == "daily_limit_breach"

    def test_overspend_prediction_triggers(self):
        with Session(engine) as session:
            # Budget $1000, already spent $1200 — guaranteed overspend
            _seed_budget(session, limit=1000, spent=1200)
            tx = _make_tx(amount=100)
            session.add(tx)
            session.commit()
            result = check_and_intervene(session, tx)
            assert result.triggered is True
            assert result.alert_type == "overspend_warning"
            assert result.predicted_overspend is not None
            assert result.predicted_overspend > 0

    def test_suggested_actions_have_defaults(self):
        with Session(engine) as session:
            _seed_budget(session, limit=1000, spent=1200)
            tx = _make_tx()
            session.add(tx)
            session.commit()
            result = check_and_intervene(session, tx)
            if result.triggered and result.suggested_actions:
                # At least one action should have a smart default
                has_default = any(a.default_value is not None for a in result.suggested_actions)
                assert has_default

    def test_duplicate_alert_suppressed(self):
        with Session(engine) as session:
            _seed_budget(session, limit=1000, spent=1200)
            tx = _make_tx()
            session.add(tx)
            session.commit()

            # First call should trigger
            result1 = check_and_intervene(session, tx)
            assert result1.triggered is True

            # Second call within cooldown should be suppressed
            result2 = check_and_intervene(session, tx)
            assert result2.triggered is False

    def test_low_severity_not_triggered(self):
        with Session(engine) as session:
            # Budget is barely over pace — should be LOW severity → no trigger
            _seed_budget(session, limit=10000, spent=100)
            tx = _make_tx(amount=10)
            session.add(tx)
            session.commit()
            result = check_and_intervene(session, tx)
            # LOW severity = no trigger
            assert result.triggered is False

    def test_loss_framed_message(self):
        with Session(engine) as session:
            _seed_budget(session, limit=1000, spent=1500)
            tx = _make_tx()
            session.add(tx)
            session.commit()
            result = check_and_intervene(session, tx)
            if result.triggered and result.message:
                # Should use loss framing words
                assert any(word in result.message.lower() for word in ["waste", "lose", "blown", "wasted", "losing"])
