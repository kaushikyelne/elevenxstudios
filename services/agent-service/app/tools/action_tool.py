"""
Action tool — lets the agent actually DO things, not just report.

Calls the financial service's action endpoints to:
- Set daily spending limits
- Toggle soft-blocks (friction layers)
- Adjust budgets
"""
import httpx
from typing import Any, Dict, Optional
from app.config import settings


async def apply_action(
    action_id: str,
    category: str,
    value: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Execute a financial action on behalf of the user.
    Called when the user agrees to a suggested action from an intervention.

    Args:
        action_id: The action to perform (set_daily_limit, soft_block, adjust_budget)
        category: The spending category to act on (e.g. Food, Transport)
        value: The limit/budget amount (for set_daily_limit and adjust_budget)
    """
    # Map action_id to endpoint
    action_endpoints = {
        "set_daily_limit": "/api/v1/actions/set-daily-limit",
        "soft_block": "/api/v1/actions/soft-block",
        "adjust_budget": "/api/v1/actions/adjust-budget",
        "keep_block": "/api/v1/actions/soft-block",
        "remove_block": "/api/v1/actions/soft-block",
        "keep_daily_limit": "/api/v1/actions/set-daily-limit",
        "adjust_daily_limit": "/api/v1/actions/set-daily-limit",
    }

    endpoint = action_endpoints.get(action_id)
    if not endpoint:
        return {"status": "error", "message": f"Unknown action: {action_id}"}

    url = f"{settings.financial_service_url}{endpoint}"

    payload = {
        "action_id": action_id,
        "category": category,
    }
    if value is not None:
        payload["value"] = value

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            return {
                "status": "error",
                "message": f"Action failed: {response.status_code} - {response.text}",
            }
    except Exception as e:
        return {"status": "error", "message": f"Could not reach financial service: {str(e)}"}
