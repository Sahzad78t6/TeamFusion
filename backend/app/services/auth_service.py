import logging
from fastapi import HTTPException
from app.database.repositories.user_repository import user_repository
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

class AuthService:
    async def signup(self, name: str, email: str, password: str) -> dict:
        logger.info(f"AuthService processing signup for email: {email}")
        if not name or not email or not password:
            raise HTTPException(status_code=400, detail="Name, email, and password are required fields.")
        
        email_clean = email.strip().lower()
        existing = await user_repository.get_by_email(email_clean)
        if existing:
            logger.warning(f"Signup failed: Duplicate email '{email_clean}'")
            raise HTTPException(status_code=400, detail="User with this email already exists.")
        
        hashed = hash_password(password)
        user_doc = await user_repository.create_user({
            "name": name.strip(),
            "email": email_clean,
            "hashed_password": hashed
        })

        access_token = create_access_token({"sub": user_doc["id"], "email": user_doc["email"]})
        refresh_token = create_refresh_token({"sub": user_doc["id"]})

        logger.info(f"User signed up successfully: {user_doc['id']}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_doc["id"],
                "name": user_doc["name"],
                "email": user_doc["email"],
                "created_at": user_doc["created_at"]
            }
        }

    async def login(self, email: str, password: str) -> dict:
        logger.info(f"AuthService processing login for email: {email}")
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required.")
            
        email_clean = email.strip().lower()
        user = await user_repository.get_by_email(email_clean)
        if not user or not verify_password(password, user["hashed_password"]):
            logger.warning(f"Login failed: Invalid credentials for '{email_clean}'")
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        
        access_token = create_access_token({"sub": user["id"], "email": user["email"]})
        refresh_token = create_refresh_token({"sub": user["id"]})

        logger.info(f"User logged in successfully: {user['id']}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "created_at": user.get("created_at")
            }
        }

    async def get_current_user(self, user_id: str) -> dict:
        user = await user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User lookup failed: user_id '{user_id}' not found")
            raise HTTPException(status_code=404, detail="User profile not found.")
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user.get("created_at")
        }

auth_service = AuthService()
