from datetime import datetime

from pydantic import BaseModel, EmailStr


class JoinRequest(BaseModel):
    email: EmailStr


class JoinResponse(BaseModel):
    message: str
    email: str
    created_at: datetime


class CountResponse(BaseModel):
    total: int
