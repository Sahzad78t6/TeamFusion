from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_token
from app.database.supabase import supabase
from app.schemas.user import UserResponse
from app.services.auth_service import _MEMORY_USERS_DB

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """
    FastAPI Dependency Injection to authenticate protected routes.
    Extracts Bearer JWT Access token, decodes payload, verifies user in DB, and returns UserResponse.
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_record = None

    # Check Supabase first
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            user_record = response.data[0]
    except Exception:
        pass

    # Check memory DB fallback
    if not user_record and user_id in _MEMORY_USERS_DB:
        user_record = _MEMORY_USERS_DB[user_id]

    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse(
        id=str(user_record["id"]),
        name=user_record["name"],
        email=user_record["email"],
        created_at=user_record.get("created_at"),
        updated_at=user_record.get("updated_at")
    )
