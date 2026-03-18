from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter(prefix="/api/v1/agent")


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")
