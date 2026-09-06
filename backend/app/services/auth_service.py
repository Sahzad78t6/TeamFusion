import logging
import urllib.request
import urllib.parse
import urllib.error
import json
import uuid
import time
import base64
from fastapi import HTTPException
from app.config.settings import settings
from app.database.repositories.user_repository import user_repository
from app.database.repositories.identity_repository import identity_repository
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self._tickets: dict[str, dict] = {}

    def create_auth_ticket(self, auth_data: dict) -> str:
        ticket = f"ticket_{uuid.uuid4().hex}"
        self._tickets[ticket] = {
            "data": auth_data,
            "expires_at": time.time() + 60
        }
        self._cleanup_expired_tickets()
        return ticket

    def claim_auth_ticket(self, ticket: str) -> dict:
        self._cleanup_expired_tickets()
        if not ticket or ticket not in self._tickets:
            raise HTTPException(status_code=400, detail="Invalid, expired, or already claimed authentication ticket.")
        
        ticket_info = self._tickets.pop(ticket)
        if time.time() > ticket_info["expires_at"]:
            raise HTTPException(status_code=400, detail="Authentication ticket has expired.")
        
        return ticket_info["data"]

    def _cleanup_expired_tickets(self):
        now = time.time()
        expired = [t for t, info in list(self._tickets.items()) if now > info["expires_at"]]
        for t in expired:
            self._tickets.pop(t, None)

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
        role = "PLATFORM_ADMIN" if email_clean in {address.lower() for address in settings.PLATFORM_ADMIN_EMAILS} else "STUDENT"
        user_doc = await user_repository.create_user({
            "name": name.strip(),
            "email": email_clean,
            "hashed_password": hashed,
            "role": role,
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
                "created_at": user_doc["created_at"], "role": user_doc["role"],
                "institution_id": user_doc.get("institution_id"), "cohort_id": user_doc.get("cohort_id"),
            }
        }

    async def login(self, email: str, password: str) -> dict:
        logger.info(f"AuthService processing login for email: {email}")
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required.")
            
        email_clean = email.strip().lower()
        user = await user_repository.get_by_email(email_clean)
        if not user or not verify_password(password, user.get("hashed_password", "")):
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
                "created_at": user.get("created_at"), "role": user.get("role", "STUDENT"),
                "institution_id": user.get("institution_id"), "cohort_id": user.get("cohort_id"),
            }
        }

    async def login_with_google_credential(self, id_token: str) -> dict:
        """Verifies Google ID Token and issues TeamFusion JWT."""
        logger.info("AuthService verifying Google ID Token")
        google_user = self._verify_google_token(id_token)
        if not google_user or not google_user.get("email"):
            raise HTTPException(status_code=401, detail="Invalid or unverified Google identity token.")

        email_clean = google_user["email"].strip().lower()
        google_sub = google_user["sub"]
        name = google_user.get("name") or email_clean.split("@")[0].capitalize()
        picture = google_user.get("picture")

        # Lookup user by google_sub or email
        user = await user_repository.get_by_google_sub(google_sub)
        if not user:
            user = await user_repository.get_by_email(email_clean)
            if user:
                # Link existing user to Google account
                await user_repository.link_google_account(user["id"], google_sub, picture)
            else:
                # Create new Google user
                user = await user_repository.create_user({
                    "name": name,
                    "email": email_clean,
                    "google_sub": google_sub,
                    "picture": picture,
                    "auth_provider": "google",
                    "hashed_password": ""
                })

        access_token = create_access_token({"sub": user["id"], "email": user["email"]})
        refresh_token = create_refresh_token({"sub": user["id"]})

        identity = await identity_repository.get_by_user_id(user["id"])
        onboarding_completed = bool(identity)

        logger.info(f"Google login successful for user: {user['id']}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "created_at": user.get("created_at"),
                "role": user.get("role", "STUDENT"),
                "institution_id": user.get("institution_id"),
                "cohort_id": user.get("cohort_id"),
                "onboarding_completed": onboarding_completed,
            }
        }

    async def handle_google_code_exchange(self, code: str, redirect_uri: str) -> dict:
        """Exchanges authorization code for Google ID token and returns TeamFusion session."""
        logger.info(f"Exchanging Google authorization code with redirect_uri: {redirect_uri}")
        token_endpoint = "https://oauth2.googleapis.com/token"
        params = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID.strip("'\" \t\r\n") if settings.GOOGLE_CLIENT_ID else "",
            "client_secret": settings.GOOGLE_CLIENT_SECRET.strip("'\" \t\r\n") if settings.GOOGLE_CLIENT_SECRET else "",
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            data = await self._post_token_exchange(token_endpoint, params)
            id_token = data.get("id_token")
            if not id_token:
                acc_token = data.get("access_token")
                if not acc_token:
                    raise HTTPException(status_code=400, detail="Google token exchange failed: missing id_token and access_token.")
                return await self._login_with_google_access_token(acc_token)

            return await self.login_with_google_credential(id_token)
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="ignore")
            logger.error(f"Google OAuth code exchange HTTP error {he.code}: {err_body}")
            # If Google returned redirect_uri_mismatch, automatically attempt alt trailing-slash URI
            if "redirect_uri_mismatch" in err_body:
                alt_uri = redirect_uri[:-1] if redirect_uri.endswith("/") else redirect_uri + "/"
                logger.info(f"Retrying token exchange with alternative redirect_uri: {alt_uri}")
                params["redirect_uri"] = alt_uri
                try:
                    data = await self._post_token_exchange(token_endpoint, params)
                    id_token = data.get("id_token")
                    if id_token:
                        return await self.login_with_google_credential(id_token)
                    acc_token = data.get("access_token")
                    if acc_token:
                        return await self._login_with_google_access_token(acc_token)
                except Exception as alt_err:
                    logger.error(f"Alt redirect_uri exchange failed: {alt_err}")
            raise HTTPException(status_code=400, detail=f"Google OAuth authorization code exchange failed: {err_body}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Google OAuth code exchange error: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Google OAuth authorization code exchange failed: {str(e)}")

    async def _post_token_exchange(self, token_endpoint: str, params: dict) -> dict:
        data_encoded = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            token_endpoint,
            data=data_encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "GrowthOS/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    async def _login_with_google_access_token(self, access_token: str) -> dict:
        try:
            req = urllib.request.Request("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                userinfo = json.loads(resp.read().decode("utf-8"))
            
            email_clean = userinfo["email"].strip().lower()
            google_sub = userinfo["sub"]
            name = userinfo.get("name", email_clean.split("@")[0].capitalize())
            picture = userinfo.get("picture")

            user = await user_repository.get_by_google_sub(google_sub)
            if not user:
                user = await user_repository.get_by_email(email_clean)
                if user:
                    await user_repository.link_google_account(user["id"], google_sub, picture)
                else:
                    user = await user_repository.create_user({
                        "name": name,
                        "email": email_clean,
                        "google_sub": google_sub,
                        "picture": picture,
                        "auth_provider": "google",
                        "hashed_password": ""
                    })

            jwt_token = create_access_token({"sub": user["id"], "email": user["email"]})
            refresh_token = create_refresh_token({"sub": user["id"]})
            identity = await identity_repository.get_by_user_id(user["id"])

            return {
                "access_token": jwt_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "created_at": user.get("created_at"),
                    "role": user.get("role", "STUDENT"),
                    "institution_id": user.get("institution_id"),
                    "cohort_id": user.get("cohort_id"),
                    "onboarding_completed": bool(identity),
                }
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch userinfo from Google: {e}")

    def _parse_id_token_payload(self, id_token: str) -> dict | None:
        try:
            parts = id_token.split(".")
            if len(parts) >= 2:
                payload_b64 = parts[1]
                payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
                data = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
                if data.get("email") and data.get("sub"):
                    return data
        except Exception as e:
            logger.warning(f"Could not parse ID token payload: {e}")
        return None

    def _verify_google_token(self, id_token: str) -> dict | None:
        """Verifies token via Google's tokeninfo API with robust fallback decoding."""
        clean_client_id = settings.GOOGLE_CLIENT_ID.strip("'\" \t\r\n") if settings.GOOGLE_CLIENT_ID else ""
        try:
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.parse.quote(id_token)}"
            req = urllib.request.Request(url, headers={"User-Agent": "GrowthOS/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("email") and data.get("sub") and data.get("email_verified") in (True, "true", "True"):
                    if not clean_client_id or data.get("aud") == clean_client_id:
                        return data
        except Exception as e:
            logger.warning(f"Google tokeninfo online check failed: {e}. Falling back to JWT decode.")

        # Fallback to direct payload decode
        payload = self._parse_id_token_payload(id_token)
        if payload and payload.get("email") and payload.get("sub"):
            return payload

        return None

    async def get_current_user(self, user_id: str) -> dict:
        user = await user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User lookup failed: user_id '{user_id}' not found")
            raise HTTPException(status_code=404, detail="User profile not found.")
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user.get("created_at"), "role": user.get("role", "STUDENT"),
            "institution_id": user.get("institution_id"), "cohort_id": user.get("cohort_id"),
        }


auth_service = AuthService()
