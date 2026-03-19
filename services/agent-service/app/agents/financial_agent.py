import logging
from typing import List, Optional

from google import genai
from google.genai import types

from app.config import settings
from app.prompts.system import FINANCIAL_ADVISOR_PROMPT
from app.tools import TOOL_FUNCTIONS, TOOL_MAP

logger = logging.getLogger(__name__)


class FinancialAgent:
    def __init__(self):
        # We use the new unified SDK
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options={'api_version': 'v1'} # Force stable v1
        )
        self.model_name = settings.gemini_model

    async def chat(self, message: str, history: Optional[List[dict]] = None) -> dict:
        """Sends a message to Gemini using the modern google-genai SDK with v1 stability."""
        
        # Priority fallback list
        models_to_try = [self.model_name, "gemini-2.0-flash", "gemini-1.5-flash"]
        
        # Format history/contents for Gemini
        contents = []
        if history:
            for h in history:
                contents.append(types.Content(role=h["role"], parts=[types.Part(text=h["content"])]))
        
        # User message
        contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

        last_error = None
        for model_id in models_to_try:
            try:
                logger.info(f"Attempting chat with model: {model_id}")
                
                # In google-genai, tools are passed as lists of functions or types.Tool
                gemini_tools = [types.Tool(function_declarations=[
                    # We can use the helper or define them. 
                    # Actually, the new SDK can auto-generate from functions too!
                ])]
                # For simplicity, let's use the functions directly if the SDK supports it, 
                # or pass the definitions we have.
                
                # Let's use the TOOL_FUNCTIONS approach if the SDK supports it.
                # Actually, the new SDK expects types.Tool objects or functions.
                
                response = self.client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=FINANCIAL_ADVISOR_PROMPT,
                        tools=TOOL_FUNCTIONS, # The new SDK supports passing functions directly!
                    ),
                )

                tool_calls_made = []
                
                # Handle potential tool calls
                while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                    part = response.candidates[0].content.parts[0]
                    fn = part.function_call
                    tool_name = fn.name
                    args = fn.args
                    
                    logger.info(f"Agent requested tool: {tool_name} with args: {args}")
                    
                    if tool_name in TOOL_MAP:
                        # Execute tool
                        result = await TOOL_MAP[tool_name](**args)
                        tool_calls_made.append({"tool": tool_name, "args": args, "result": result})
                        
                        # Add the model's call and our response to the conversation
                        contents.append(response.candidates[0].content)
                        contents.append(types.Content(
                            parts=[types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=result
                                )
                            )]
                        ))
                        
                        # Generate next turn
                        response = self.client.models.generate_content(
                            model=model_id,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=FINANCIAL_ADVISOR_PROMPT,
                            ),
                        )
                    else:
                        break

                return {
                    "reply": response.text,
                    "tool_calls": tool_calls_made
                }

            except Exception as e:
                last_error = e
                # Handle 404 or 429 fallbacks
                if "404" in str(e) or "429" in str(e):
                    logger.warning(f"Model {model_id} failed with {e}, trying fallback...")
                    continue
                break

        return {"reply": f"Sorry, all models failed. Last error: {str(last_error)}", "tool_calls": []}
