import uuid
import logging
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.database.mongodb import get_database
from app.database.collections import COLLECTION_USERS
from app.schemas.user import UserSignup, UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshTokenResponse, MessageResponse
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, decode_token

# Setup standard logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def signup(user_in: UserSignup) -> TokenResponse:
        """
        User Signup Service (MongoDB):
        - Check duplicate email in MongoDB
        - Hash password with bcrypt
        - Create user document in MongoDB users collection
        - Issue Access & Refresh Tokens
        """
        email_clean = user_in.email.lower().strip()
        logger.info(f"Incoming signup request for: {email_clean}")

        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection not initialized"
            )
            
        users_collection = db[COLLECTION_USERS]

        # Check existing user in MongoDB
        try:
            existing_user = await users_collection.find_one({"email": email_clean})
            if existing_user:
                logger.warning(f"Signup failed: Email {email_clean} already exists.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database error during duplicate email check: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error during validation: {str(e)}"
            )

        # Hash password & generate tokens
        password_hashed = get_password_hash(user_in.password)
        logger.info("Password hashed successfully.")
        
        user_id = str(uuid.uuid4())
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        logger.info("JWT tokens generated successfully.")

        now_iso = datetime.now(timezone.utc).isoformat()
        new_user_record = {
            "_id": user_id,
            "id": user_id,
            "name": user_in.name.strip(),
            "email": email_clean,
            "password_hash": password_hashed,
            "refresh_token": refresh_token,
            "created_at": now_iso,
            "updated_at": now_iso
        }

        # Insert into MongoDB users collection
        try:
            await users_collection.insert_one(new_user_record)
            logger.info(f"User {email_clean} inserted successfully into database.")
        except Exception as e:
            logger.error(f"Database error during user insert: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database insert error: {str(e)}"
            )

        user_response = UserResponse(
            id=user_id,
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
        User Login Service (MongoDB):
        - Verify email existence in MongoDB
        - Verify bcrypt password hash
        - Issue new Access Token & Refresh Token
        """
        email_clean = credentials.email.lower().strip()
        logger.info(f"Incoming login request for: {email_clean}")
        
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
            user_record = await users_collection.find_one({"email": email_clean})
            if user_record:
                logger.info(f"User {email_clean} found in database.")
            else:
                logger.warning(f"Login failed: Email {email_clean} not found.")
        except Exception as e:
            logger.error(f"Database error during user fetch: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database fetch error: {str(e)}"
            )

        if not user_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify bcrypt hash
        if not verify_password(credentials.password, user_record["password_hash"]):
            logger.warning(f"Login failed: Incorrect password for {email_clean}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Password verified successfully for {email_clean}.")

        user_id = str(user_record["id"])
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        logger.info("JWT tokens generated successfully on login.")

        now_iso = datetime.now(timezone.utc).isoformat()

        # Update refresh token in MongoDB
        try:
            update_res = await users_collection.update_one(
                {"id": user_id},
                {"$set": {"refresh_token": refresh_token, "updated_at": now_iso}}
            )
            
            if update_res.modified_count == 0:
                logger.warning("Update operation modified 0 documents, but user might be updated.")
            else:
                logger.info(f"Refresh token updated for {email_clean}.")
        except Exception as e:
            logger.error(f"Database error during refresh token update: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database update error: {str(e)}"
            )

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
        logger.info("Incoming token refresh request.")
        payload = decode_token(token_in)
        token_type = payload.get("type")
        if token_type != "refresh":
            logger.warning("Token refresh failed: Invalid token type.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Refresh token required."
            )

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token refresh failed: Missing user ID in payload.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        new_access_token = create_access_token(subject=user_id)
        logger.info(f"New access token issued for user ID {user_id}.")
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer"
        )

    @staticmethod
    async def logout(user_id: str) -> MessageResponse:
        """
        User Logout Service (MongoDB):
        - Invalidate refresh token in database
        """
        logger.info(f"Incoming logout request for user ID: {user_id}")
        
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection not initialized"
            )
            
        users_collection = db[COLLECTION_USERS]
        
        try:
            await users_collection.update_one(
                {"id": user_id},
                {"$set": {"refresh_token": None, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            logger.info(f"Successfully logged out user ID: {user_id}")
        except Exception as e:
            logger.error(f"Database error during logout: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database update error during logout: {str(e)}"
            )

        return MessageResponse(message="Successfully logged out")
