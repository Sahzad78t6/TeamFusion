import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.database.supabase import supabase
from app.schemas.user import UserSignup, UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshTokenResponse, MessageResponse
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, decode_token


class AuthService:
    @staticmethod
    async def signup(user_in: UserSignup) -> TokenResponse:
        """
        User Signup Service:
        - Check duplicate email
        - Hash password with bcrypt
        - Create user record in Supabase users table
        - Issue Access & Refresh Tokens
        """
        email_clean = user_in.email.lower().strip()

        # Check existing user in Supabase
        try:
            existing = supabase.table("users").select("id").eq("email", email_clean).execute()
            if existing.data and len(existing.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists"
                )
        except HTTPException:
            raise
        except Exception as e:
            # Table fallback or DB exception handling
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

        try:
            insert_res = supabase.table("users").insert(new_user_record).execute()
            if not insert_res.data or len(insert_res.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to register user in database"
                )
            created_user = insert_res.data[0]
        except Exception as e:
            # Handle Supabase duplicate key or write error
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error during user registration: {str(e)}"
            )

        user_response = UserResponse(
            id=str(created_user["id"]),
            name=created_user["name"],
            email=created_user["email"],
            created_at=created_user.get("created_at"),
            updated_at=created_user.get("updated_at")
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
        - Verify email existence
        - Verify bcrypt password hash
        - Issue new Access Token & Refresh Token
        """
        email_clean = credentials.email.lower().strip()

        try:
            res = supabase.table("users").select("*").eq("email", email_clean).execute()
            if not res.data or len(res.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user_record = res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query error during login: {str(e)}"
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

        # Update refresh token in DB
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            supabase.table("users").update({
                "refresh_token": refresh_token,
                "updated_at": now_iso
            }).eq("id", user_id).execute()
        except Exception as e:
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
        - Verify active user record in DB
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

        # Check DB for valid refresh token
        try:
            res = supabase.table("users").select("id, refresh_token").eq("id", user_id).execute()
            if not res.data or len(res.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            db_refresh_token = res.data[0].get("refresh_token")
            if db_refresh_token and db_refresh_token != token_in:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked or invalidated"
                )
        except HTTPException:
            raise
        except Exception as e:
            pass

        new_access_token = create_access_token(subject=user_id)
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer"
        )

    @staticmethod
    async def logout(user_id: str) -> MessageResponse:
        """
        User Logout Service:
        - Invalidate refresh token in database
        """
        try:
            supabase.table("users").update({
                "refresh_token": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", user_id).execute()
        except Exception as e:
            pass

        return MessageResponse(message="Successfully logged out")
