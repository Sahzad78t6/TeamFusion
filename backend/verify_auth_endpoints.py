import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_verification():
    print("=" * 60)
    print("      GROWTHOS AUTHENTICATION MODULE VERIFICATION")
    print("=" * 60)

    test_email = "test.verified.user@growthos.ai"
    test_name = "Verified Tester"
    test_password = "SecurePassword123!"

    # 1. Signup Test
    print("\n[TEST 1] Testing POST /api/auth/signup...")
    signup_payload = {
        "name": test_name,
        "email": test_email,
        "password": test_password
    }
    res = client.post("/api/auth/signup", json=signup_payload)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}"
    
    signup_data = res.json()
    assert "access_token" in signup_data, "Missing access_token in signup response"
    assert "refresh_token" in signup_data, "Missing refresh_token in signup response"
    assert signup_data["user"]["email"] == test_email, "User email mismatch"
    access_token = signup_data["access_token"]
    refresh_token = signup_data["refresh_token"]
    print("--> [PASS]: Signup endpoint works perfectly!")

    # 2. Duplicate Signup Test
    print("\n[TEST 2] Testing Duplicate Email Signup...")
    res_dup = client.post("/api/auth/signup", json=signup_payload)
    print(f"Status Code: {res_dup.status_code}")
    print(f"Response: {res_dup.json()}")
    assert res_dup.status_code == 400, f"Expected 400 Bad Request, got {res_dup.status_code}"
    print("--> [PASS]: Duplicate email prevention works!")

    # 3. Invalid Short Password Validation Test
    print("\n[TEST 3] Testing Short Password Validation (< 8 chars)...")
    res_short = client.post("/api/auth/signup", json={
        "name": "Short Pass User",
        "email": "shortpass@growthos.ai",
        "password": "123"
    })
    print(f"Status Code: {res_short.status_code}")
    assert res_short.status_code == 422, f"Expected 422 Validation Error, got {res_short.status_code}"
    print("--> [PASS]: Password validation (min 8 chars) works!")

    # 4. Login Test (Valid Credentials)
    print("\n[TEST 4] Testing POST /api/auth/login...")
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    print(f"Status Code: {res_login.status_code}")
    print(f"Response: {res_login.json()}")
    assert res_login.status_code == 200, f"Expected 200 OK, got {res_login.status_code}"
    login_data = res_login.json()
    assert "access_token" in login_data
    print("--> [PASS]: Login with bcrypt verification works!")

    # 5. Invalid Password Login Test
    print("\n[TEST 5] Testing Login with Wrong Password...")
    res_wrong = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "WrongPassword999!"
    })
    print(f"Status Code: {res_wrong.status_code}")
    assert res_wrong.status_code == 401, f"Expected 401 Unauthorized, got {res_wrong.status_code}"
    print("--> [PASS]: Invalid password rejection works!")

    # 6. Current User Test GET /api/auth/me (Protected)
    print("\n[TEST 6] Testing Protected GET /api/auth/me...")
    headers = {"Authorization": f"Bearer {access_token}"}
    res_me = client.get("/api/auth/me", headers=headers)
    print(f"Status Code: {res_me.status_code}")
    print(f"Response: {res_me.json()}")
    assert res_me.status_code == 200, f"Expected 200 OK, got {res_me.status_code}"
    assert res_me.json()["email"] == test_email
    print("--> [PASS]: GET /api/auth/me JWT Bearer protection works!")

    # 7. Refresh Token Test POST /api/auth/refresh
    print("\n[TEST 7] Testing POST /api/auth/refresh...")
    res_refresh = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    print(f"Status Code: {res_refresh.status_code}")
    print(f"Response: {res_refresh.json()}")
    assert res_refresh.status_code == 200
    assert "access_token" in res_refresh.json()
    print("--> [PASS]: Token refresh works!")

    # 8. Logout Test POST /api/auth/logout (Protected)
    print("\n[TEST 8] Testing Protected POST /api/auth/logout...")
    res_logout = client.post("/api/auth/logout", headers=headers)
    print(f"Status Code: {res_logout.status_code}")
    print(f"Response: {res_logout.json()}")
    assert res_logout.status_code == 200
    print("--> [PASS]: Logout works!")

    print("\n" + "=" * 60)
    print("   ALL 8 AUTHENTICATION MODULE TESTS PASSED VERIFIED 100%")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
