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

def test_protected_endpoint_rejects_missing_bearer_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
