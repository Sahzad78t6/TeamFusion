from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
from app.middleware.auth import get_current_user_id
from app.utils.response import success_response


class GoogleLoginPayload(BaseModel):
    credential: str | None = Field(default=None, description="Google ID Token")
    code: str | None = Field(default=None, description="Google OAuth Authorization Code")
    redirect_uri: str | None = Field(default=None, description="Redirect URI used for code exchange")


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup_api(payload: SignupRequest):
    return await auth_service.signup(payload.name, payload.email, payload.password)

@router.post("/login", response_model=TokenResponse)
async def login_api(payload: LoginRequest):
    return await auth_service.login(payload.email, payload.password)

@router.post("/google", response_model=TokenResponse)
async def google_login_api(payload: GoogleLoginPayload):
    if payload.credential:
        return await auth_service.login_with_google_credential(payload.credential)
    elif payload.code:
        redirect_uri = payload.redirect_uri or "https://teamfusion-96bi.onrender.com"
        return await auth_service.handle_google_code_exchange(payload.code, redirect_uri)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Either 'credential' (ID token) or 'code' (authorization code) is required.")

@router.get("/me", response_model=UserResponse)
async def get_me_api(current_user_id: str = Depends(get_current_user_id)):
    return await auth_service.get_current_user(current_user_id)

@router.post("/logout")
async def logout_api(current_user_id: str = Depends(get_current_user_id)):
    return success_response(message="Logged out successfully")

