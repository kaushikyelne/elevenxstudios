"""
Real-time overspend predictor.

Given a category budget, projects end-of-month spending based on current pace.
Uses loss framing: "You'll WASTE ₹X" not "You'll overspend ₹X".
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from app.models import Budget
from app.schemas import PredictionResponse, InterventionSeverity


def predict_overspend(session: Session, category: str) -> Optional[PredictionResponse]:
    """
    Projects month-end spending for a given category.
    Returns None if no budget exists for this category.
    """
    budget = session.exec(
        select(Budget).where(Budget.category == category)
    ).first()

    if not budget or budget.limit_amount <= 0:
        return None

    now = datetime.utcnow()
    days_elapsed = max(now.day, 1)  # At least 1 to avoid division by zero
    days_in_month = _days_in_month(now.year, now.month)
    days_remaining = days_in_month - days_elapsed

    # Spending pace: daily average × total days
    daily_pace = budget.spent_amount / days_elapsed
    predicted_total = daily_pace * days_in_month
    predicted_overspend = max(predicted_total - budget.limit_amount, 0)

    # Pace multiplier: how fast are they burning vs budget allows
    budget_daily_allowance = budget.limit_amount / days_in_month
    pace_multiplier = round(daily_pace / budget_daily_allowance, 2) if budget_daily_allowance > 0 else 0

    # Severity based on predicted overspend percentage
    overspend_percentage = (predicted_overspend / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
    severity = _calculate_severity(overspend_percentage, budget.spent_amount / budget.limit_amount * 100)

    return PredictionResponse(
        category=category,
        current_spent=budget.spent_amount,
        limit=budget.limit_amount,
        predicted_total=round(predicted_total, 2),
        predicted_overspend=round(predicted_overspend, 2),
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        pace_multiplier=pace_multiplier,
        severity=severity,
    )


def predict_all(session: Session) -> list[PredictionResponse]:
    """Projects overspending for all budgeted categories."""
    budgets = session.exec(select(Budget)).all()
    predictions = []
    for budget in budgets:
        pred = predict_overspend(session, budget.category)
        if pred and pred.predicted_overspend > 0:
            predictions.append(pred)
    return predictions


def _calculate_severity(overspend_pct: float, used_pct: float) -> InterventionSeverity:
    """
    Severity escalation logic:
    - LOW:      predicted overspend < 10% OR budget usage < 60%
    - MEDIUM:   predicted overspend 10-25% OR usage 60-85%
    - HIGH:     predicted overspend 25-50% OR usage 85-100%
    - CRITICAL: predicted overspend > 50% OR already over budget
    """
    if used_pct > 100 or overspend_pct > 50:
        return InterventionSeverity.CRITICAL
    elif used_pct > 85 or overspend_pct > 25:
        return InterventionSeverity.HIGH
    elif used_pct > 60 or overspend_pct > 10:
        return InterventionSeverity.MEDIUM
    else:
        return InterventionSeverity.LOW


def _days_in_month(year: int, month: int) -> int:
    """Returns number of days in a given month."""
    import calendar
    return calendar.monthrange(year, month)[1]
