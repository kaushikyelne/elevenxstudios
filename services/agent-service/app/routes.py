from fastapi import APIRouter, Depends
from app.schemas import HealthResponse, ChatRequest, ChatResponse
from app.agents.financial_agent import FinancialAgent

router = APIRouter(prefix="/api/v1/agent")


def get_agent():
    return FinancialAgent()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, agent: FinancialAgent = Depends(get_agent)):
    """Interact with the MoneyLane Financial Assistant."""
    result = await agent.chat(req.message, req.history)
    return ChatResponse(
        reply=result["reply"],
        tool_calls=result["tool_calls"]
    )
