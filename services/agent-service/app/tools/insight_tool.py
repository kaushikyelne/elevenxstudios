import httpx
from typing import Any, Dict
from app.config import settings

async def get_top_insight() -> Dict[str, Any]:
    """
    Fetch the most relevant financial insight for the user.
    Provides diagnostic and prescriptive context for the agent.
    """
    url = f"{settings.financial_service_url}/api/v1/insights/home"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
    return {"state": "error", "message": "Insight engine unavailable"}
