from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None


class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any]
    result: Any


class ChatResponse(BaseModel):
    reply: str
    tool_calls: List[ToolCall] = []
