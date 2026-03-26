"""
Action execution endpoints — the Action Layer.

This is the missing moat: users can actually DO things, not just get reports.
Soft-block replaces naive block-category — the system adds friction, not fake control.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Budget, BehaviorLog
from app.schemas import ActionRequest, ActionResponse, BehaviorFeedback
from app.database import get_session
from datetime import datetime

router = APIRouter()


@router.post("/set-daily-limit", response_model=ActionResponse)
async def set_daily_limit(req: ActionRequest, session: Session = Depends(get_session)):
    """Set a daily spending cap for a category."""
    budget = session.exec(
        select(Budget).where(Budget.category == req.category)
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail=f"No budget found for {req.category}")

    if not req.value or req.value <= 0:
        raise HTTPException(status_code=400, detail="Daily limit must be a positive number")

    budget.daily_limit = req.value
    session.add(budget)
    session.commit()

    # Log the behavior
    _log_action(session, req.category, "set_daily_limit", req.action_id)

    return ActionResponse(
        success=True,
        message=f"Daily limit for {req.category} set to ₹{req.value:.0f}. You'll get alerts if you exceed this.",
        category=req.category,
        action_id="set_daily_limit",
    )


@router.post("/soft-block", response_model=ActionResponse)
async def soft_block(req: ActionRequest, session: Session = Depends(get_session)):
    """
    Toggle spending freeze for a category.
    This is a "friction layer" — not a real block (we can't control UPI).
    It triggers warnings on every transaction in this category.
    """
    budget = session.exec(
        select(Budget).where(Budget.category == req.category)
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail=f"No budget found for {req.category}")

    # Toggle
    budget.is_blocked = not budget.is_blocked
    session.add(budget)
    session.commit()

    _log_action(session, req.category, "soft_block", req.action_id)

    state = "activated" if budget.is_blocked else "removed"
    return ActionResponse(
        success=True,
        message=f"Spending freeze for {req.category} {state}. You'll get a warning on every {req.category} transaction.",
        category=req.category,
        action_id="soft_block",
    )


@router.post("/adjust-budget", response_model=ActionResponse)
async def adjust_budget(req: ActionRequest, session: Session = Depends(get_session)):
    """Adjust the monthly budget limit for a category."""
    budget = session.exec(
        select(Budget).where(Budget.category == req.category)
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail=f"No budget found for {req.category}")

    if not req.value or req.value <= 0:
        raise HTTPException(status_code=400, detail="Budget limit must be a positive number")

    old_limit = budget.limit_amount
    budget.limit_amount = req.value
    session.add(budget)
    session.commit()

    _log_action(session, req.category, "adjust_budget", req.action_id)

    direction = "increased" if req.value > old_limit else "decreased"
    return ActionResponse(
        success=True,
        message=f"{req.category} budget {direction} from ₹{old_limit:.0f} to ₹{req.value:.0f}.",
        category=req.category,
        action_id="adjust_budget",
    )


@router.post("/feedback")
async def record_feedback(feedback: BehaviorFeedback, session: Session = Depends(get_session)):
    """
    Record user's response to an intervention — the behavioral feedback loop.
    This is the moat: over time, we learn what works for this user.
    """
    log = session.get(BehaviorLog, feedback.intervention_id)
    if not log:
        raise HTTPException(status_code=404, detail="Intervention not found")

    log.action_taken = feedback.action_taken
    log.ignored = not feedback.action_taken
    log.action_id = feedback.action_id
    log.resolved_at = datetime.utcnow()
    session.add(log)
    session.commit()

    return {"status": "recorded", "intervention_id": feedback.intervention_id}


def _log_action(session: Session, category: str, intervention_type: str, action_id: str):
    """Log that a user took action — feeds the behavioral feedback loop."""
    log = BehaviorLog(
        category=category,
        intervention_type=intervention_type,
        action_taken=True,
        action_id=action_id,
        ignored=False,
        resolved_at=datetime.utcnow(),
    )
    session.add(log)
    session.commit()
