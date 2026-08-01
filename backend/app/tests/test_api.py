from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_dashboard_endpoint():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert "analytics" in response.json()
