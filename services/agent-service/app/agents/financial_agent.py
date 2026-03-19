import logging
from typing import List, Optional

import google.generativeai as genai
from google.generativeai import types

from app.config import settings
from app.prompts.system import FINANCIAL_ADVISOR_PROMPT
from app.tools import TOOL_FUNCTIONS, TOOL_MAP

logger = logging.getLogger(__name__)


class FinancialAgent:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        
    async def chat(self, message: str, history: Optional[List[dict]] = None) -> dict:
        """Sends a message to Gemini using stable SDK with model fallback."""
        
        # Priority list of models to try
        models_to_try = [
            self.model_name,
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp"
        ]
        
        last_error = None
        
        for model_id in models_to_try:
            try:
                logger.info(f"Attempting chat with model: {model_id}")
                model = genai.GenerativeModel(
                    model_name=model_id,
                    system_instruction=FINANCIAL_ADVISOR_PROMPT,
                    tools=TOOL_FUNCTIONS
                )

                # Format history
                history_list = []
                if history:
                    for h in history:
                        history_list.append({"role": h["role"], "parts": [h["content"]]})
                
                chat_session = model.start_chat(history=history_list)
                
                # Send message
                response = await chat_session.send_message_async(message)
                
                tool_calls_made = []
                
                # ReAct Loop
                while response.candidates[0].content.parts[0].function_call:
                    fn = response.candidates[0].content.parts[0].function_call
                    tool_name = fn.name
                    args = dict(fn.args)
                    
                    if tool_name in TOOL_MAP:
                        result = await TOOL_MAP[tool_name](**args)
                        tool_calls_made.append({"tool": tool_name, "args": args, "result": result})
                        
                        response = await chat_session.send_message_async(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=result
                                )
                            )
                        )
                    else:
                        break

                return {
                    "reply": response.text,
                    "tool_calls": tool_calls_made
                }

            except Exception as e:
                last_error = e
                # If it's a 404, we try the next model
                if "404" in str(e) or "not found" in str(e).lower():
                    logger.warning(f"Model {model_id} not found, trying fallback...")
                    continue
                # For 429 (quota), we might also want to try another model, but often quota is project-wide
                if "429" in str(e):
                    logger.warning(f"Model {model_id} rate limited, trying fallback...")
                    continue
                
                # For other errors, break and report
                break

        return {"reply": f"Sorry, all models failed. Last error: {str(last_error)}", "tool_calls": []}

        except Exception as e:
            logger.error(f"Error in FinancialAgent.chat: {e}", exc_info=True)
            return {"reply": f"Sorry, I encountered an error: {str(e)}", "tool_calls": []}
