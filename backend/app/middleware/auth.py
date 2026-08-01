from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_token
from app.database.supabase import supabase
from app.schemas.user import UserResponse

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
        
    # Query user from Supabase database
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User associated with token not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_data = response.data[0]
        return UserResponse(
            id=str(user_data["id"]),
            name=user_data["name"],
            email=user_data["email"],
            created_at=user_data.get("created_at"),
            updated_at=user_data.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query error during authentication: {str(e)}"
        )
