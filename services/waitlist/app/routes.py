from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import CountResponse, JoinRequest, JoinResponse
from app.service import get_count, join_waitlist

router = APIRouter(prefix="/api/v1/waitlist")


@router.post("/join", response_model=JoinResponse)
async def join(req: JoinRequest, db: AsyncSession = Depends(get_db)):
    entry, is_new = await join_waitlist(db, req.email)
    return JoinResponse(
        message="Welcome to the waitlist!" if is_new else "You're already on the list.",
        email=entry.email,
        created_at=entry.created_at,
    )


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/count", response_model=CountResponse)
async def count(db: AsyncSession = Depends(get_db)):
    total = await get_count(db)
    return CountResponse(total=total)
