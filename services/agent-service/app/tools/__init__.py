from app.tools.transaction_tool import get_transactions
from app.tools.notification_tool import send_notification
from app.tools.insight_tool import get_top_insight

# List of all available tool functions for Google GenAI introspection
TOOL_FUNCTIONS = [
    get_transactions,
    send_notification,
    get_top_insight,
]

# Map for manual execution if needed
TOOL_MAP = {
    "get_transactions": get_transactions,
    "send_notification": send_notification,
    "get_top_insight": get_top_insight,
}
