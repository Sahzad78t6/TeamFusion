import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import auth_service
from app.database.repositories.user_repository import user_repository

client = TestClient(app)

def test_root_health_check_preservation():
    """Verify root GET / returns standard health check when no OAuth params exist."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "online"
    assert "app" in data

@pytest.mark.asyncio
async def test_google_login_with_mocked_id_token():
    """Verify login_with_google_credential successfully validates Google ID token and returns JWT token."""
    mock_id_info = {
        "sub": "google_test_12345",
        "email": "testgoogleuser@gmail.com",
        "name": "Test Google User",
        "picture": "https://example.com/avatar.jpg"
    }

    mock_user = {
        "id": "mongo_user_999",
        "email": "testgoogleuser@gmail.com",
        "name": "Test Google User",
        "google_sub": "google_test_12345",
        "picture": "https://example.com/avatar.jpg"
    }

    with patch.object(auth_service, "_verify_google_token", return_value=mock_id_info):
        with patch.object(user_repository, "get_by_google_sub", new_callable=AsyncMock) as mock_get_sub, \
             patch.object(user_repository, "get_by_email", new_callable=AsyncMock) as mock_get_email, \
             patch.object(user_repository, "create_user", new_callable=AsyncMock) as mock_create_user:
            
            mock_get_sub.return_value = None
            mock_get_email.return_value = None
            mock_create_user.return_value = mock_user

            result = await auth_service.login_with_google_credential("mock_valid_google_id_token")

            assert "access_token" in result
            assert "refresh_token" in result
            assert result["user"]["email"] == "testgoogleuser@gmail.com"

def test_google_auth_api_endpoint_failure():
    """Verify POST /api/auth/google handles invalid payload gracefully."""
    response = client.post("/api/auth/google", json={})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_ticket_creation_and_claiming():
    """Verify single-use tickets can be created and claimed exactly once."""
    mock_session = {
        "access_token": "mock_jwt_access_token",
        "refresh_token": "mock_jwt_refresh_token",
        "token_type": "bearer",
        "user": {"id": "usr_123", "email": "test@example.com"}
    }
    ticket = auth_service.create_auth_ticket(mock_session)
    assert ticket.startswith("ticket_")
    
    # Claim ticket
    claimed = auth_service.claim_auth_ticket(ticket)
    assert claimed["access_token"] == "mock_jwt_access_token"
    
    # Second claim should fail
    with pytest.raises(Exception):
        auth_service.claim_auth_ticket(ticket)

def test_claim_ticket_api_endpoint():
    """Verify POST /api/auth/claim-ticket endpoint works end-to-end."""
    mock_session = {
        "access_token": "test_token_999",
        "refresh_token": "test_refresh_999",
        "token_type": "bearer",
        "user": {"id": "usr_999", "name": "Claim User", "email": "claim@example.com"}
    }
    ticket = auth_service.create_auth_ticket(mock_session)
    response = client.post("/api/auth/claim-ticket", json={"ticket": ticket})
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "test_token_999"

@pytest.mark.asyncio
async def test_root_oauth_callback_redirect():
    """Verify GET / with code creates ticket and redirects to production Vercel frontend."""
    mock_auth_res = {
        "access_token": "prod_jwt_token",
        "refresh_token": "prod_refresh_token",
        "token_type": "bearer",
        "user": {"id": "u_test", "email": "test@gmail.com", "onboarding_completed": True}
    }
    with patch.object(auth_service, "handle_google_code_exchange", new_callable=AsyncMock, return_value=mock_auth_res):
        response = client.get("/?code=valid_google_code&state=prod", follow_redirects=False)
        assert response.status_code == 302
        location = response.headers.get("location", "")
        assert "https://team-fusion-psi.vercel.app/dashboard?ticket=ticket_" in location
        assert "localhost" not in location

