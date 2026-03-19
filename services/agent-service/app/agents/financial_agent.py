import logging
from typing import List, Optional

import google.generativeai as genai
from google.generativeai import types

from app.config import settings
from app.prompts.system import FINANCIAL_ADVISOR_PROMPT
from app.tools import get_tool_definitions, get_tool_map

logger = logging.getLogger(__name__)


class FinancialAgent:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.tool_map = get_tool_map()
        
        # Tools in Gemini format for the older SDK
        self.tools = get_tool_definitions()

    async def chat(self, message: str, history: Optional[List[dict]] = None) -> dict:
        """Sends a message to Gemini 1.5/2.0 using the stable generativeai SDK."""
        
        try:
            # Initialize model with system instruction and tools
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=FINANCIAL_ADVISOR_PROMPT,
                tools=self.tools
            )

            # Start chat session with history if provided
            history_list = []
            if history:
                for h in history:
                    history_list.append({"role": h["role"], "parts": [h["content"]]})
            
            chat_session = model.start_chat(history=history_list)
            
            # Send the user message
            response = await chat_session.send_message_async(message)
            
            # ReAct Loop: Handle Tool Calls
            tool_calls_made = []
            
            # The older SDK handles the first turn, but if it returns a function call, we must execute.
            candidate = response.candidates[0]
            
            # Check for function calls in the response parts
            for part in candidate.content.parts:
                if fn := part.function_call:
                    tool_name = fn.name
                    args = dict(fn.args)
                    
                    logger.info(f"Agent requested tool: {tool_name} with args: {args}")
                    
                    if tool_name in self.tool_map:
                        tool_result = await self.tool_map[tool_name].execute(**args)
                        tool_calls_made.append({"tool": tool_name, "args": args, "result": tool_result})
                        
                        # Provide the result back to the model for final answer
                        response = await chat_session.send_message_async(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_result
                                )
                            )
                        )
                    else:
                        logger.warning(f"Tool {tool_name} requested but not found in map.")

            return {
                "reply": response.text,
                "tool_calls": tool_calls_made
            }

        except Exception as e:
            logger.error(f"Error in FinancialAgent.chat: {e}", exc_info=True)
            return {"reply": f"Sorry, I encountered an error: {str(e)}", "tool_calls": []}
