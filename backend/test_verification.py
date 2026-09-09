import time
import requests

BASE_URL = "http://localhost:8000"
test_email = f"verification_test_{int(time.time())}@growthos.io"
signup_payload = {
    "name": "Alex Johnson",
    "email": test_email,
    "password": "SecurePassword123!"
}

def run_tests():
    print("--- 1. POST /auth/signup ---")
    r1 = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload)
    print(f"Status: {r1.status_code}")
    d1 = r1.json()
    print("Response keys:", list(d1.keys()))
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {d1}"
    assert "access_token" in d1 and d1["access_token"], "Missing access_token"
    assert d1["user"]["role"] == "STUDENT", f"Expected role STUDENT, got {d1['user']['role']}"
    assert d1["user"]["onboarding_completed"] is False, f"Expected onboarding_completed False, got {d1['user']['onboarding_completed']}"
    token = d1["access_token"]
    print("Step 1 PASSED: access_token present, user.role == 'STUDENT', onboarding_completed == False\n")

    print("--- 2. GET /auth/me ---")
    headers = {"Authorization": f"Bearer {token}"}
    r2 = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {r2.status_code}")
    d2 = r2.json()
    print("Response:", d2)
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}: {d2}"
    assert d2["id"] == d1["user"]["id"]
    assert d2["name"] == d1["user"]["name"]
    assert d2["email"] == d1["user"]["email"]
    assert d2["role"] == "STUDENT"
    assert d2["onboarding_completed"] is False
    print("Step 2 PASSED: GET /auth/me returns same user object shape unwrapped\n")

    print("--- 3. POST /auth/signup again with SAME email ---")
    r3 = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload)
    print(f"Status: {r3.status_code}")
    d3 = r3.json()
    print("Response:", d3)
    assert r3.status_code == 400, f"Expected 400, got {r3.status_code}: {d3}"
    assert d3.get("detail") == "Email already registered", f"Expected 'Email already registered', got {d3}"
    print("Step 3 PASSED: Duplicate email returns HTTP 400 with 'Email already registered'\n")

    print("--- 4. POST /onboarding and verify GET /auth/me ---")
    onboarding_payload = {
        "goal": "ml_engineer",
        "target_role": "ml_engineer",
        "current_role": "2nd Year",
        "skills": ["Stanford University"],
        "interests": ["AI", "Robotics"],
        "experience": "2nd Year",
        "learning_style": "visual",
        "available_time": "10 hours/week",
        "preferred_content": ["video", "hands-on"],
        "language": "English"
    }
    r4 = requests.post(f"{BASE_URL}/onboarding", json=onboarding_payload, headers=headers)
    print(f"Status POST /onboarding: {r4.status_code}")
    d4 = r4.json()
    print("Response:", d4)
    assert r4.status_code == 200, f"Expected 200, got {r4.status_code}: {d4}"
    assert d4["onboarding_completed"] is True, "Expected onboarding_completed to be True"

    r4_me = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status GET /auth/me: {r4_me.status_code}")
    d4_me = r4_me.json()
    print("Response:", d4_me)
    assert r4_me.status_code == 200
    assert d4_me["onboarding_completed"] is True, "Expected onboarding_completed to be True in GET /auth/me"

    # Verify GET /onboarding/identity
    r_ident = requests.get(f"{BASE_URL}/onboarding/identity", headers=headers)
    print(f"Status GET /onboarding/identity: {r_ident.status_code}")
    d_ident = r_ident.json()
    print("Identity response:", d_ident)
    assert r_ident.status_code == 200
    assert d_ident["goal"] == "ml_engineer"
    assert d_ident["year"] == "2nd Year"
    assert d_ident["college"] == "Stanford University"
    assert d_ident["target_role"] == "ml_engineer"

    # Verify POST /auth/logout
    r_logout = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"Status POST /auth/logout: {r_logout.status_code}")
    assert r_logout.status_code == 200
    assert r_logout.json() == {}
    print("Step 4 PASSED: POST /onboarding updates user, GET /auth/me confirms onboarding_completed == True, identity and logout work\n")

if __name__ == "__main__":
    run_tests()
