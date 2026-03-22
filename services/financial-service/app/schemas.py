from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class TransactionBase(BaseModel):
    model_config = {"from_attributes": True}

    amount: float
    description: str
    category: str
    date: datetime
    merchant: Optional[str] = None


# --- Insight Engine (existing, unchanged) ---

class InsightResponse(BaseModel):
    title: str
    description: str
    confidence: float
    impact: float
    score: float = 0.0
    actions: List[str]
    dynamic_prompts: List[str]
    state: Optional[str] = "ready"  # no_data, ready


class BudgetStatus(BaseModel):
    category: str
    limit_amount: float
    spent_amount: float
    percentage_used: float
    status_color: str  # Green, Yellow, Red


# --- Intervention Engine (new) ---

class InterventionSeverity(str, Enum):
    LOW = "low"        # FYI — no push
    MEDIUM = "medium"  # Subtle nudge
    HIGH = "high"      # Push notification
    CRITICAL = "critical"  # Aggressive + repeated


class ActionSuggestion(BaseModel):
    """A concrete, 1-tap action the user can take."""
    action_id: str       # e.g. "set_daily_limit", "adjust_budget"
    label: str           # e.g. "Set ₹300/day limit"
    description: str     # e.g. "Caps your daily food spending at ₹300"
    default_value: Optional[float] = None  # Pre-computed smart default
    confidence: float = 0.8  # How confident we are this is the right action


class InterventionResponse(BaseModel):
    """Returned alongside a transaction when an intervention is triggered."""
    triggered: bool
    severity: InterventionSeverity = InterventionSeverity.LOW
    alert_type: Optional[str] = None  # overspend_warning, daily_limit_breach, pace_alert
    message: Optional[str] = None     # Loss-framed message
    predicted_overspend: Optional[float] = None
    days_remaining: Optional[int] = None
    suggested_actions: List[ActionSuggestion] = []


class TransactionCreateResponse(BaseModel):
    """Extended response for POST /transactions — includes intervention data."""
    transaction: TransactionBase
    intervention: InterventionResponse


class PredictionResponse(BaseModel):
    """Overspend prediction for a single category."""
    category: str
    current_spent: float
    limit: float
    predicted_total: float
    predicted_overspend: float
    days_elapsed: int
    days_remaining: int
    pace_multiplier: float  # >1.0 = overspending pace
    severity: InterventionSeverity


class ActionRequest(BaseModel):
    """Request to execute an action."""
    action_id: str  # set_daily_limit, soft_block, adjust_budget
    category: str
    value: Optional[float] = None  # The limit/budget amount


class ActionResponse(BaseModel):
    """Response after executing an action."""
    success: bool
    message: str
    category: str
    action_id: str


class BehaviorFeedback(BaseModel):
    """User's response to an intervention — closes the feedback loop."""
    intervention_id: int
    action_taken: bool
    action_id: Optional[str] = None
