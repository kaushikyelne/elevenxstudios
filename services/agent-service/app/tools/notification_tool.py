import uuid
import httpx
import logging
from typing import Any, Dict
from app.tools.base import AgentTool
from app.config import settings

logger = logging.getLogger(__name__)


class SendNotificationTool(AgentTool):
    @property
    def name(self) -> str:
        return "send_notification"

    @property
    def description(self) -> str:
        return "Send an email notification or alert to the user. Use this for reminders, budget warnings, or status updates."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message content of the notification",
                },
                "email": {
                    "type": "string",
                    "description": "The recipient email address",
                },
                "event_type": {
                    "type": "string",
                    "description": "The type of alert (e.g., 'BUDGET_EXCEEDED', 'REMINDER')",
                },
            },
            "required": ["message", "email"],
        }

    async def execute(self, message: str, email: str, event_type: str = "AGENT_ALERT") -> Any:
        url = settings.notification_service_url
        if not url:
            return {"status": "error", "message": "Notification service not configured"}
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json={
                    "event_id": str(uuid.uuid4()),
                    "event_type": event_type,
                    "email": email,
                    "metadata": {"content": message},
                })
                response.raise_for_status()
                return {"status": "success", "response": response.json()}
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {"status": "failed", "error": str(e)}
