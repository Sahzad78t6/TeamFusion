from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_token
from app.database.mongodb import get_database
from app.database.collections import COLLECTION_USERS
from app.schemas.user import UserResponse

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """
    FastAPI Dependency Injection to authenticate protected routes.
    Extracts Bearer JWT Access token, decodes payload, verifies user in MongoDB, and returns UserResponse.
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
        
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection not initialized"
        )
        
    users_collection = db[COLLECTION_USERS]
    user_record = None

    # Check MongoDB
    try:
        user_record = await users_collection.find_one({"id": user_id})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while authenticating user: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
