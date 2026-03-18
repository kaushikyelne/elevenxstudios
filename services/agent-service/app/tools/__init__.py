from typing import List
from app.tools.base import AgentTool
from app.tools.transaction_tool import GetTransactionsTool
from app.tools.notification_tool import SendNotificationTool

# Registry of all available tools for the agent
TOOL_REGISTRY: List[AgentTool] = [
    GetTransactionsTool(),
    SendNotificationTool(),
]

def get_tool_definitions() -> List[dict]:
    """Returns a list of tool definitions in Gemini format."""
    return [t.to_gemini_tool() for t in TOOL_REGISTRY]

def get_tool_map() -> dict:
    """Returns a map of tool names to their instances for execution."""
    return {t.name: t for t in TOOL_REGISTRY}
