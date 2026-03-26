import logging
import httpx
from typing import List, Optional, Dict, Any

from app.config import settings
from app.prompts.system import FINANCIAL_COPILOT_PROMPT
from app.tools import TOOL_MAP

logger = logging.getLogger(__name__)


class FinancialAgent:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model or "gemini-2.0-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def chat(self, message: str, history: Optional[List[dict]] = None) -> dict:
        """Sends a message to Gemini using the direct REST API (v1beta)."""

        # Simplified: 2 models max, not 4
        models_to_try = [self.model_name, "gemini-1.5-flash-latest"]

        last_error = None
        for model_id in models_to_try:
            try:
                url = f"{self.base_url}/models/{model_id}:generateContent?key={self.api_key}"

                # 1. Fetch situational context (Top Insight)
                insight_context = ""
                try:
                    from app.tools.insight_tool import get_top_insight
                    top_insight = await get_top_insight()
                    if top_insight.get("state") == "ready":
                        insight_context = (
                            f"\n\nCURRENT FINANCIAL INSIGHT: {top_insight['title']} - "
                            f"{top_insight['description']}. "
                            f"Actions suggested: {', '.join(top_insight['actions'])}."
                        )
                except Exception as e:
                    logger.warning(f"Could not fetch insight context: {e}")

                # 2. Prepare contents
                contents = []
                if history:
                    for h in history:
                        contents.append({
                            "role": "user" if h["role"] == "user" else "model",
                            "parts": [{"text": h["content"]}]
                        })

                contents.append({
                    "role": "user",
                    "parts": [{"text": message}]
                })

                # 3. Prepare Tools — focused set: get, insight, act, notify
                tools = [
                    {
                        "function_declarations": [
                            {
                                "name": "get_transactions",
                                "description": "Fetch recent financial transactions. Use this for spending or history questions.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "days": {"type": "INTEGER", "description": "Number of days (default 30)"},
                                        "category": {"type": "STRING", "description": "Category filter"}
                                    }
                                }
                            },
                            {
                                "name": "get_top_insight",
                                "description": "Fetch the most relevant financial insight for the user. Provides diagnostic and prescriptive context.",
                                "parameters": {"type": "OBJECT", "properties": {}}
                            },
                            {
                                "name": "apply_action",
                                "description": "Execute a financial action: set daily spending limit, toggle spending freeze, or adjust budget. Use when the user agrees to a suggested action.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "action_id": {
                                            "type": "STRING",
                                            "description": "Action to perform: set_daily_limit, soft_block, adjust_budget"
                                        },
                                        "category": {
                                            "type": "STRING",
                                            "description": "Spending category (e.g. Food, Transport)"
                                        },
                                        "value": {
                                            "type": "NUMBER",
                                            "description": "Amount for the limit or budget (required for set_daily_limit and adjust_budget)"
                                        }
                                    },
                                    "required": ["action_id", "category"]
                                }
                            },
                            {
                                "name": "send_notification",
                                "description": "Send an email alert. Use this for reminders or budget warnings.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "message": {"type": "STRING", "description": "Alert content"},
                                        "email": {"type": "STRING", "description": "Recipient email"},
                                        "event_type": {"type": "STRING", "description": "Type of alert"}
                                    },
                                    "required": ["message", "email"]
                                }
                            }
                        ]
                    }
                ]

                payload = {
                    "contents": contents,
                    "system_instruction": {"parts": [{"text": FINANCIAL_COPILOT_PROMPT + insight_context}]},
                    "tools": tools
                }

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)

                    if response.status_code == 404:
                        logger.warning(f"Model {model_id} not found, trying fallback...")
                        continue

                    if response.status_code == 429:
                        logger.warning(f"Quota exceeded for {model_id}, trying fallback...")
                        continue

                    if response.status_code != 200:
                        logger.error(f"Gemini API Error: {response.status_code} - {response.text}")
                        last_error = f"{response.status_code}: {response.text}"
                        continue

                    data = response.json()

                    if "candidates" not in data or not data["candidates"]:
                        return {"reply": "No response from AI.", "tool_calls": []}

                    content = data["candidates"][0]["content"]
                    tool_calls_made = []

                    # Handle Tool Calls
                    for part in content.get("parts", []):
                        if "functionCall" in part:
                            fn = part["functionCall"]
                            tool_name = fn["name"]
                            args = fn.get("args", {})

                            logger.info(f"Agent tool call: {tool_name}({args})")

                            if tool_name in TOOL_MAP:
                                result = await TOOL_MAP[tool_name](**args)
                                tool_calls_made.append({"tool": tool_name, "args": args, "result": result})

                                contents.append(content)
                                contents.append({
                                    "role": "function",
                                    "parts": [{
                                        "functionResponse": {
                                            "name": tool_name,
                                            "response": {"name": tool_name, "content": result}
                                        }
                                    }]
                                })

                                final_payload = {
                                    "contents": contents,
                                    "system_instruction": {"parts": [{"text": FINANCIAL_COPILOT_PROMPT}]}
                                }
                                final_res = await client.post(url, json=final_payload)
                                final_data = final_res.json()

                                if "candidates" in final_data:
                                    reply = final_data["candidates"][0]["content"]["parts"][0].get("text", "Done.")
                                    return {"reply": reply, "tool_calls": tool_calls_made}

                    reply = content["parts"][0].get("text", "I'm not sure how to answer that.")
                    return {"reply": reply, "tool_calls": tool_calls_made}

            except Exception as e:
                logger.error(f"Agent exception for {model_id}: {e}")
                last_error = e
                continue

        return {"reply": f"Sorry, all models failed. Last error: {str(last_error)}", "tool_calls": []}
