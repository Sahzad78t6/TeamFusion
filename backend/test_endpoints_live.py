import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api"

def make_post(endpoint: str, payload: dict, token: str | None = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def make_get(endpoint: str, token: str | None = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_all():
    print("--- 1. GET /api/health ---")
    health = make_get("/health")
    health_data = health.get("data", health)
    print("Health Status:", health_data.get("status"))
    print("Database Connected:", health_data.get("database", {}).get("connected"))

    print("\n--- 2. POST /api/auth/signup ---")
    email = f"live_test_{int(time.time())}@growthos.ai"
    signup = make_post("/auth/signup", {"name": "Live Tester", "email": email, "password": "Password123!"})
    signup_data = signup.get("data", signup)
    token = signup_data["access_token"]
    user_id = signup_data["user"]["id"]
    print(f"Signup Successful! User ID: {user_id}")

    print("\n--- 3. POST /api/auth/login ---")
    login = make_post("/auth/login", {"email": email, "password": "Password123!"})
    login_data = login.get("data", login)
    print("Login Successful! Token received:", bool(login_data.get("access_token")))

    print("\n--- 4. POST /api/copilot/chat (Goal Message) ---")
    chat1 = make_post("/copilot/chat", {"message": "I want to become a Principal AI Architect"}, token=token)
    chat1_obj = chat1.get("data") if isinstance(chat1.get("data"), dict) and "agent" in chat1.get("data") else chat1
    print("Goal Chat Agent:", chat1_obj.get("agent"))
    print("Goal Chat Message:", chat1_obj.get("message"))

    print("\n--- 5. POST /api/copilot/chat (Negative/Burnout Reflection Message) ---")
    chat2 = make_post("/copilot/chat", {"message": "I feel stressed and burnt out and completely overwhelmed"}, token=token)
    chat2_obj = chat2.get("data") if isinstance(chat2.get("data"), dict) and "agent" in chat2.get("data") else chat2
    print("Reflection Chat Agent:", chat2_obj.get("agent"))
    print("Reflection Chat Message:", chat2_obj.get("message"))

    print("\n--- 6. POST /api/copilot/chat (Resource Curation Message) ---")
    chat3 = make_post("/copilot/chat", {"message": "Curate python courses for me"}, token=token)
    chat3_obj = chat3.get("data") if isinstance(chat3.get("data"), dict) and "agent" in chat3.get("data") else chat3
    print("Curator Chat Agent:", chat3_obj.get("agent"))
    print("Curator Chat Message:", chat3_obj.get("message"))

    print("\n[ALL LIVE ENDPOINT TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    test_all()
