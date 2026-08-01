from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from app.middleware.auth import get_current_user_id
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.services.copilot_service import copilot_service
from app.exceptions import LLMUnavailableError, LLMJSONParseError, GrowthOSError

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])

@router.post("/chat", response_model=CopilotResponse)
async def chat_with_copilot(
    payload: CopilotRequest,
    user_id: str = Depends(get_current_user_id),
    raise_on_error: bool = False
):
    try:
        return await copilot_service.respond(user_id, payload.message.strip(), raise_on_error=raise_on_error)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}"
        )
    except (LLMUnavailableError, LLMJSONParseError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Service Unavailable: {e}"
        )
    except GrowthOSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
