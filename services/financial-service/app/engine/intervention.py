"""
Proactive Intervention Engine.

Called on every transaction write. Detects threshold breaches
and fires alerts with loss-framed messaging and 1-click action suggestions.
No LLM in this path — deterministic, fast, cheap.
"""
import logging
import httpx
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from app.models import Budget, Alert, Transaction
from app.schemas import (
    InterventionResponse, InterventionSeverity, ActionSuggestion,
)
from app.engine.predictor import predict_overspend
from app.config import settings

logger = logging.getLogger(__name__)

# Cooldown: don't re-alert the same category+type within this window
ALERT_COOLDOWN_HOURS = 24


async def check_and_intervene(
    session: Session,
    transaction: Transaction,
) -> InterventionResponse:
    """
    Main entry point — called after every transaction commit.
    Checks budgets, predicts overspending, and returns intervention if needed.
    """
    category = transaction.category
    no_intervention = InterventionResponse(triggered=False)

    budget = session.exec(
        select(Budget).where(Budget.category == category)
    ).first()

    if not budget:
        return no_intervention

    # --- Check 1: Category soft-blocked ---
    if budget.is_blocked:
        return await _build_intervention(
            session=session,
            category=category,
            alert_type="soft_block",
            severity=InterventionSeverity.HIGH,
            message=(
                f"⚠️ You set a spending freeze on {category}. "
                f"This ₹{transaction.amount:.0f} transaction just went through. "
                f"Want to keep the freeze active?"
            ),
            predicted_overspend=None,
            days_remaining=None,
            actions=[
                ActionSuggestion(
                    action_id="keep_block",
                    label=f"Keep {category} freeze",
                    description=f"Maintain the spending freeze on {category}",
                    confidence=0.9,
                ),
                ActionSuggestion(
                    action_id="remove_block",
                    label=f"Remove {category} freeze",
                    description=f"Lift the spending freeze and allow {category} transactions",
                    confidence=0.3,
                ),
            ],
        )

    # --- Check 2: Daily limit breach ---
    if budget.daily_limit and budget.daily_limit > 0:
        today_spent = _get_today_spent(session, category)
        if today_spent > budget.daily_limit:
            overage = today_spent - budget.daily_limit
            return await _build_intervention(
                session=session,
                category=category,
                alert_type="daily_limit_breach",
                severity=InterventionSeverity.HIGH,
                message=(
                    f"🚨 You've spent ₹{today_spent:.0f} on {category} today — "
                    f"that's ₹{overage:.0f} over your ₹{budget.daily_limit:.0f} daily limit. "
                    f"Every extra ₹ today is money you're losing from this month's budget."
                ),
                predicted_overspend=overage,
                days_remaining=None,
                actions=[
                    ActionSuggestion(
                        action_id="keep_daily_limit",
                        label=f"Keep ₹{budget.daily_limit:.0f}/day cap",
                        description=f"Stay disciplined. No more {category} spending today.",
                        confidence=0.85,
                    ),
                    ActionSuggestion(
                        action_id="adjust_daily_limit",
                        label="Increase daily limit",
                        description=f"Raise daily {category} cap (current: ₹{budget.daily_limit:.0f})",
                        default_value=round(budget.daily_limit * 1.25),
                        confidence=0.4,
                    ),
                ],
            )

    # --- Check 3: Predictive overspend ---
    prediction = predict_overspend(session, category)
    if prediction and prediction.predicted_overspend > 0:
        pct_used = (budget.spent_amount / budget.limit_amount * 100)

        # Loss-framed message — "waste" not "overspend"
        message = _build_loss_framed_message(
            category=category,
            predicted_overspend=prediction.predicted_overspend,
            days_remaining=prediction.days_remaining,
            pct_used=pct_used,
            pace_multiplier=prediction.pace_multiplier,
        )

        # Smart default: calculate a daily limit that keeps them within budget
        remaining_budget = max(budget.limit_amount - budget.spent_amount, 0)
        suggested_daily = round(remaining_budget / max(prediction.days_remaining, 1))

        return await _build_intervention(
            session=session,
            category=category,
            alert_type="overspend_warning",
            severity=prediction.severity,
            message=message,
            predicted_overspend=prediction.predicted_overspend,
            days_remaining=prediction.days_remaining,
            actions=[
                ActionSuggestion(
                    action_id="set_daily_limit",
                    label=f"Set ₹{suggested_daily}/day limit",
                    description=(
                        f"Caps daily {category} spending at ₹{suggested_daily} to stay within budget."
                    ),
                    default_value=suggested_daily,
                    confidence=0.82,
                ),
                ActionSuggestion(
                    action_id="adjust_budget",
                    label="Increase budget",
                    description=f"Raise {category} budget from ₹{budget.limit_amount:.0f}",
                    default_value=round(budget.limit_amount * 1.2),
                    confidence=0.35,
                ),
            ],
        )

    return no_intervention


def _build_loss_framed_message(
    category: str,
    predicted_overspend: float,
    days_remaining: int,
    pct_used: float,
    pace_multiplier: float,
) -> str:
    """
    Loss framing: same data, 3x impact.
    "You'll WASTE ₹2400" > "You'll overspend ₹2400"
    """
    if pct_used > 100:
        return (
            f"🔴 You've already blown through your {category} budget. "
            f"You're ₹{predicted_overspend:.0f} over with {days_remaining} days left. "
            f"Every additional spend is money wasted."
        )
    elif pace_multiplier > 1.5:
        return (
            f"🔴 At this pace, you'll waste ₹{predicted_overspend:.0f} on {category} this month. "
            f"You're spending {pace_multiplier:.1f}x faster than your budget allows. "
            f"{days_remaining} days to course-correct."
        )
    elif pace_multiplier > 1.0:
        return (
            f"⚠️ You're on track to waste ₹{predicted_overspend:.0f} on {category} this month. "
            f"You've used {pct_used:.0f}% of your budget with {days_remaining} days remaining."
        )
    else:
        return (
            f"ℹ️ {category} spending is trending slightly high. "
            f"Projected overspend: ₹{predicted_overspend:.0f} if pace continues."
        )


async def _build_intervention(
    session: Session,
    category: str,
    alert_type: str,
    severity: InterventionSeverity,
    message: str,
    predicted_overspend: Optional[float],
    days_remaining: Optional[int],
    actions: list[ActionSuggestion],
) -> InterventionResponse:
    """
    Builds an InterventionResponse and records the alert (with cooldown dedup).
    Only fires for MEDIUM+ severity. LOW = silent/FYI.
    """
    # Don't fire for LOW severity
    if severity == InterventionSeverity.LOW:
        return InterventionResponse(triggered=False)

    # Cooldown: check if we already alerted this category+type recently
    if _was_recently_alerted(session, category, alert_type):
        logger.info(f"Suppressed duplicate alert: {alert_type} for {category}")
        return InterventionResponse(triggered=False)

    # Record the alert
    alert = Alert(
        category=category,
        alert_type=alert_type,
        severity=severity.value,
        message=message,
    )
    session.add(alert)
    session.commit()

    # Fire actual notification if HIGH or CRITICAL
    if severity in [InterventionSeverity.HIGH, InterventionSeverity.CRITICAL]:
        await _fire_notification(message, alert_type)

    return InterventionResponse(
        triggered=True,
        severity=severity,
        alert_type=alert_type,
        message=message,
        predicted_overspend=predicted_overspend,
        days_remaining=days_remaining,
        suggested_actions=actions,
    )


async def _fire_notification(message: str, event_type: str):
    """Calls the internal Notification Service (Go/Brevo)."""
    url = settings.notification_service_url
    if not url:
        logger.warning("Notification Service URL not configured. Skipping alert.")
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            payload = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type.upper(),
                "email": "user@example.com",  # In a real app, this would be the user's email
                "metadata": {"content": message},
            }
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Proactive notification sent: {event_type}")
    except Exception as e:
        logger.error(f"Failed to fire proactive notification: {e}")


def _was_recently_alerted(session: Session, category: str, alert_type: str) -> bool:
    """Check if an alert of this type was sent for this category within the cooldown window."""
    cutoff = datetime.utcnow() - timedelta(hours=ALERT_COOLDOWN_HOURS)
    existing = session.exec(
        select(Alert).where(
            Alert.category == category,
            Alert.alert_type == alert_type,
            Alert.sent_at >= cutoff,
        )
    ).first()
    return existing is not None


def _get_today_spent(session: Session, category: str) -> float:
    """Sum of all transactions in a category for today."""
    today = datetime.utcnow().date()
    transactions = session.exec(
        select(Transaction).where(Transaction.category == category)
    ).all()
    return sum(
        tx.amount for tx in transactions
        if tx.date.date() == today
    )
