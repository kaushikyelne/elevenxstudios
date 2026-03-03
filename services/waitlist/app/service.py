import logging

import httpx
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import WaitlistEntry

logger = logging.getLogger(__name__)


async def join_waitlist(db: AsyncSession, email: str) -> tuple[WaitlistEntry, bool]:
    """Join the waitlist. Returns (entry, is_new).

    Idempotent — duplicate email returns the existing entry.
    Handles race conditions via IntegrityError catch.
    """
    normalized = email.lower().strip()

    # Check if already exists
    result = await db.execute(
        select(WaitlistEntry).where(func.lower(WaitlistEntry.email) == normalized)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing, False

    try:
        entry = WaitlistEntry(email=normalized)
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
    except IntegrityError:
        # Race condition: another request inserted the same email between
        # our SELECT and INSERT. Roll back and fetch the existing entry.
        await db.rollback()
        result = await db.execute(
            select(WaitlistEntry).where(func.lower(WaitlistEntry.email) == normalized)
        )
        return result.scalar_one(), False

    # Fire-and-forget notification (post-commit)
    await _notify(normalized)

    return entry, True


async def get_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count(WaitlistEntry.id)))
    return result.scalar_one()


async def _notify(email: str) -> None:
    """Post to notification service if configured. Never block or raise."""
    url = settings.notification_service_url
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json={"type": "waitlist_joined", "email": email})
    except Exception:
        logger.warning("Notification failed for %s — continuing", email, exc_info=True)
