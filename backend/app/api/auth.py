from fastapi import APIRouter, Depends, Header
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
from app.middleware.auth import get_current_user_id
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup_api(payload: SignupRequest):
    return await auth_service.signup(payload.name, payload.email, payload.password)

@router.post("/login", response_model=TokenResponse)
async def login_api(payload: LoginRequest):
    return await auth_service.login(payload.email, payload.password)

@router.get("/me", response_model=UserResponse)
async def get_me_api(current_user_id: str = Depends(get_current_user_id)):
    return await auth_service.get_current_user(current_user_id)

@router.post("/logout")
async def logout_api(current_user_id: str = Depends(get_current_user_id)):
    return success_response(message="Logged out successfully")
