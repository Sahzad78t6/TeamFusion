from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user_id
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.services.copilot_service import copilot_service

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


@router.post("/chat", response_model=CopilotResponse)
async def chat_with_copilot(payload: CopilotRequest, user_id: str = Depends(get_current_user_id)):
    return await copilot_service.respond(user_id, payload.message.strip())
