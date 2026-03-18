import logging
from typing import List, Optional

from google import genai
from google.genai import types

from app.config import settings
from app.prompts.system import FINANCIAL_ADVISOR_PROMPT
from app.tools import get_tool_definitions, get_tool_map

logger = logging.getLogger(__name__)


class FinancialAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_id = settings.gemini_model
        self.tool_map = get_tool_map()
        
        # Tools in Gemini format
        self.gemini_tools = [
            types.Tool(function_declarations=[
                types.FunctionDeclaration(**t) for t in get_tool_definitions()
            ])
        ]

    async def chat(self, message: str, history: Optional[List[dict]] = None) -> dict:
        """Sends a message to Gemini and handles potential tool calls."""
        
        # Format history for Gemini
        contents = []
        if history:
            for h in history:
                contents.append(types.Content(role=h["role"], parts=[types.Part(text=h["content"])]))
        
        # Add current message
        contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

        try:
            # Initial call to Gemini
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=FINANCIAL_ADVISOR_PROMPT,
                    tools=self.gemini_tools,
                ),
            )

            # Recursive tool handling loop (ReAct)
            # Note: For simplicity, we handle one round of tool calls.
            # Gemini typically suggests the tools in the first response.
            
            final_parts = []
            tool_calls_made = []

            for part in response.candidates[0].content.parts:
                if part.function_call:
                    tool_call = part.function_call
                    tool_name = tool_call.name
                    args = tool_call.args
                    
                    logger.info(f"Agent requested tool: {tool_name} with args: {args}")
                    
                    if tool_name in self.tool_map:
                        tool_result = await self.tool_map[tool_name].execute(**args)
                        tool_calls_made.append({"tool": tool_name, "args": args, "result": tool_result})
                        
                        # Add tool response to contents for final generation
                        contents.append(response.candidates[0].content)
                        contents.append(types.Content(
                            parts=[types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_result
                                )
                            )]
                        ))
                    else:
                        logger.warning(f"Tool {tool_name} requested but not found in map.")

            # If tool calls were made, generate the final response with tool results
            if tool_calls_made:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=FINANCIAL_ADVISOR_PROMPT,
                    ),
                )

            reply = response.text
            return {
                "reply": reply,
                "tool_calls": tool_calls_made
            }

        except Exception as e:
            logger.error(f"Error in FinancialAgent.chat: {e}", exc_info=True)
            return {"reply": f"Sorry, I encountered an error: {str(e)}", "tool_calls": []}
