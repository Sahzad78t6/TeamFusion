from fastapi.testclient import TestClient
from app.main import app
from app.utils.jwt import create_access_token

client = TestClient(app)
auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'test_user_id'})}"}

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_dashboard_endpoint():
    response = client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert "analytics" in response.json()

def test_analytics_endpoint():
    response = client.get("/api/analytics", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    data = response.json()["data"]
    assert "growth_score" in data
    assert "burnout_risk_score" in data

def test_planner_task_toggle_endpoint():
    response = client.patch("/api/planner/tasks/task_123", json={"completed": True}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["completed"] is True

def test_notification_read_endpoint():
    client.get("/api/dashboard", headers=auth_headers)
    response = client.patch("/api/notification/notif_123/read", headers=auth_headers)
    assert response.status_code == 200
    assert "success" in response.json()
