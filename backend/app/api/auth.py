import urllib.parse
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
from app.config.settings import settings
from app.middleware.auth import get_current_user_id
from app.utils.response import success_response


class GoogleLoginPayload(BaseModel):
    credential: str | None = Field(default=None, description="Google ID Token")
    code: str | None = Field(default=None, description="Google OAuth Authorization Code")
    redirect_uri: str | None = Field(default=None, description="Redirect URI used for code exchange")


class TicketClaimPayload(BaseModel):
    ticket: str = Field(..., description="Single-use OAuth exchange ticket")


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup_api(payload: SignupRequest):
    return await auth_service.signup(payload.name, payload.email, payload.password)

@router.post("/login", response_model=TokenResponse)
async def login_api(payload: LoginRequest):
    return await auth_service.login(payload.email, payload.password)

@router.post("/claim-ticket", response_model=TokenResponse)
async def claim_ticket_api(payload: TicketClaimPayload):
    return auth_service.claim_auth_ticket(payload.ticket)

@router.post("/google", response_model=TokenResponse)
async def google_login_api(payload: GoogleLoginPayload):
    if payload.credential:
        return await auth_service.login_with_google_credential(payload.credential)
    elif payload.code:
        redirect_uri = payload.redirect_uri or settings.GOOGLE_OAUTH_REDIRECT_URI
        return await auth_service.handle_google_code_exchange(payload.code, redirect_uri)
    else:
        raise HTTPException(status_code=400, detail="Either 'credential' (ID token) or 'code' (authorization code) is required.")

@router.get("/google/login")
async def google_login_redirect(state: str | None = "prod"):
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured on the backend server.")
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={urllib.parse.quote(client_id)}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote('openid email profile')}&"
        f"state={urllib.parse.quote(state or 'prod')}&"
        f"prompt=select_account"
    )
    return RedirectResponse(url=auth_url, status_code=302)

@router.get("/me", response_model=UserResponse)
async def get_me_api(current_user_id: str = Depends(get_current_user_id)):
    return await auth_service.get_current_user(current_user_id)

@router.post("/logout")
async def logout_api(current_user_id: str = Depends(get_current_user_id)):
    return success_response(message="Logged out successfully")
