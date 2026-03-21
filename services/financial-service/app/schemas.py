from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    description: str
    category: str
    date: datetime
    merchant: Optional[str] = None

class InsightResponse(BaseModel):
    title: str
    description: str
    confidence: float
    impact: float
    score: float = 0.0
    actions: List[str]
    dynamic_prompts: List[str]
    state: Optional[str] = "ready" # no_data, ready

class BudgetStatus(BaseModel):
    category: str
    limit_amount: float
    spent_amount: float
    percentage_used: float
    status_color: str # Green, Yellow, Red
