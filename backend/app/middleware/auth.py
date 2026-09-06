from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_token
from app.database.repositories.user_repository import user_repository

security_bearer = HTTPBearer(auto_error=False)

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    return payload["sub"]

async def get_current_user(user_id: str = Depends(get_current_user_id)) -> dict:
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Session user no longer exists.")
    return user

def require_roles(*roles: str):
    async def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role", "STUDENT") not in roles:
            raise HTTPException(status_code=403, detail="Your role is not permitted to perform this action.")
        return user
    return dependency
