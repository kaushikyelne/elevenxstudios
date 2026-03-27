import httpx
from typing import Any, Dict, Optional
from app.config import settings

async def get_transactions(days: int = 30, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch a list of recent financial transactions for the user.
    """
    url = f"{settings.financial_service_url}/api/v1/transactions/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            transactions = response.json()
            if category:
                transactions = [tx for tx in transactions if tx["category"].lower() == category.lower()]
            return {"transactions": transactions[:days]}
    return {"transactions": [], "error": "Financial service unavailable"}
