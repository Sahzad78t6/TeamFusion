from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_token

security_bearer = HTTPBearer(auto_error=False)

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)) -> str:
    if not credentials:
        # For seamless dev/testing default to demo user id if unauthenticated
        return "demo_user_123"
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    return payload["sub"]
