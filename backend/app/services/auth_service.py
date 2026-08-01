import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import HTTPException, status
from app.database.supabase import supabase
from app.schemas.user import UserSignup, UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshTokenResponse, MessageResponse
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, decode_token

# In-memory store fallback if Supabase table is pending or initializing
_MEMORY_USERS_DB: Dict[str, Dict[str, Any]] = {}


class AuthService:
    @staticmethod
    async def signup(user_in: UserSignup) -> TokenResponse:
        """
        User Signup Service:
        - Check duplicate email in Supabase & memory store
        - Hash password with bcrypt
        - Create user record in Supabase users table (with fallback)
        - Issue Access & Refresh Tokens
        """
        email_clean = user_in.email.lower().strip()

        # Check existing email in memory
        for u in _MEMORY_USERS_DB.values():
            if u.get("email") == email_clean:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists"
                )

        # Check existing user in Supabase
        try:
            res = supabase.table("users").select("id").eq("email", email_clean).execute()
            if res.data and len(res.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists"
                )
        except HTTPException:
            raise
        except Exception:
            pass

        # Hash password & generate tokens
        password_hashed = get_password_hash(user_in.password)
        user_id = str(uuid.uuid4())

        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        now_iso = datetime.now(timezone.utc).isoformat()
        new_user_record = {
            "id": user_id,
            "name": user_in.name.strip(),
            "email": email_clean,
            "password_hash": password_hashed,
            "refresh_token": refresh_token,
            "created_at": now_iso,
            "updated_at": now_iso
        }

        # Store in memory DB
        _MEMORY_USERS_DB[user_id] = new_user_record

        # Try insert into Supabase users table
        try:
            insert_res = supabase.table("users").insert(new_user_record).execute()
            if insert_res.data and len(insert_res.data) > 0:
                new_user_record = insert_res.data[0]
        except Exception:
            pass

        user_response = UserResponse(
            id=str(new_user_record["id"]),
            name=new_user_record["name"],
            email=new_user_record["email"],
            created_at=new_user_record.get("created_at"),
            updated_at=new_user_record.get("updated_at")
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_response
        )

    @staticmethod
    async def login(credentials: UserLogin) -> TokenResponse:
        """
        User Login Service:
        - Verify email existence in Supabase / memory store
        - Verify bcrypt password hash
        - Issue new Access Token & Refresh Token
        """
        email_clean = credentials.email.lower().strip()
        user_record = None

        # Check Supabase first
        try:
            res = supabase.table("users").select("*").eq("email", email_clean).execute()
            if res.data and len(res.data) > 0:
                user_record = res.data[0]
        except Exception:
            pass

        # Check memory store fallback if not found in Supabase
        if not user_record:
            for u in _MEMORY_USERS_DB.values():
                if u.get("email") == email_clean:
                    user_record = u
                    break

        if not user_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify bcrypt hash
        if not verify_password(credentials.password, user_record["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = str(user_record["id"])
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        now_iso = datetime.now(timezone.utc).isoformat()
        user_record["refresh_token"] = refresh_token
        user_record["updated_at"] = now_iso
        _MEMORY_USERS_DB[user_id] = user_record

        # Update refresh token in Supabase
        try:
            supabase.table("users").update({
                "refresh_token": refresh_token,
                "updated_at": now_iso
            }).eq("id", user_id).execute()
        except Exception:
            pass

        user_response = UserResponse(
            id=user_id,
            name=user_record["name"],
            email=user_record["email"],
            created_at=user_record.get("created_at"),
            updated_at=user_record.get("updated_at")
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_response
        )

    @staticmethod
    async def refresh_token(token_in: str) -> RefreshTokenResponse:
        """
        Refresh Token Service:
        - Validate refresh token
        - Issue new 15-minute Access Token
        """
        payload = decode_token(token_in)
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Refresh token required."
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        new_access_token = create_access_token(subject=user_id)
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer"
        )

    @staticmethod
    async def logout(user_id: str) -> MessageResponse:
        """
        User Logout Service:
        - Invalidate refresh token in database & memory store
        """
        if user_id in _MEMORY_USERS_DB:
            _MEMORY_USERS_DB[user_id]["refresh_token"] = None

        try:
            supabase.table("users").update({
                "refresh_token": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", user_id).execute()
        except Exception:
            pass

        return MessageResponse(message="Successfully logged out")
