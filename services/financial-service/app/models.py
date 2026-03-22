from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, JSON
from enum import Enum


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: str
    category: str
    date: datetime = Field(default_factory=datetime.utcnow)
    merchant: Optional[str] = None
    manual_override: bool = Field(default=False)


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True, unique=True)
    limit_amount: float
    spent_amount: float = Field(default=0.0)
    daily_limit: Optional[float] = Field(default=None)
    is_blocked: bool = Field(default=False)
    month: int = Field(default_factory=lambda: datetime.utcnow().month)
    year: int = Field(default_factory=lambda: datetime.utcnow().year)


class CategoryRule(SQLModel, table=True):
    """Rule-based categorization for transactions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    category: str


class Alert(SQLModel, table=True):
    """Tracks sent alerts to prevent notification spam."""
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True)
    alert_type: str  # overspend_warning, daily_limit_breach, pace_alert
    severity: str  # low, medium, high, critical
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)


class BehaviorLog(SQLModel, table=True):
    """Tracks user responses to interventions — the feedback loop."""
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True)
    intervention_type: str  # overspend_warning, daily_limit_breach, pace_alert
    action_taken: bool = Field(default=False)
    action_id: Optional[str] = None  # Which action they chose, if any
    ignored: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
