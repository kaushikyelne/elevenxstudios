from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, JSON

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
    month: int = Field(default_factory=lambda: datetime.utcnow().month)
    year: int = Field(default_factory=lambda: datetime.utcnow().year)

class CategoryRule(SQLModel, table=True):
    """Rule-based categorization for transactions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    category: str
