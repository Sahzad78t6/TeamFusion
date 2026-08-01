from fastapi import APIRouter, Depends, status
from app.schemas.user import UserSignup, UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshTokenRequest, RefreshTokenResponse, MessageResponse
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserSignup):
    """
    User Signup Endpoint:
    Registers a new user, hashes password with bcrypt, stores record in Supabase, and returns JWT access/refresh tokens.
    """
    return await AuthService.signup(user_in)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin):
    """
    User Login Endpoint:
    Verifies user credentials against bcrypt hash and issues access & refresh tokens.
    """
    return await AuthService.login(credentials)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get Current User Endpoint (Protected):
    Requires valid JWT Access Token in Authorization Bearer header.
    Returns authenticated user profile information.
    """
    return current_user


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh Token Endpoint:
    Exchanges a valid refresh token for a new 15-minute Access Token.
    """
    return await AuthService.refresh_token(request.refresh_token)


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    User Logout Endpoint (Protected):
    Invalidates stored refresh token for current authenticated user.
    """
    return await AuthService.logout(current_user.id)
