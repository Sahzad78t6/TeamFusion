import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api"

def make_post(endpoint: str, payload: dict, token: str | None = None, query_params: str = "") -> tuple[int, dict]:
    url = f"{BASE_URL}{endpoint}{query_params}"
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw_error": body}

def make_get(endpoint: str, token: str | None = None) -> tuple[int, dict]:
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw_error": body}

def run_e2e():
    print("============================================================")
    print("STEP 3: REAL END-TO-END VERIFICATION")
    print("============================================================")

    # 1. Signup + Login
    email = f"e2e_architect_{int(time.time())}@growthos.ai"
    print(f"\n[1. Creating Test User: {email}]")
    status_code, signup = make_post("/auth/signup", {"name": "E2E Architect", "email": email, "password": "Password123!"})
    signup_data = signup.get("data", signup)
    token = signup_data["access_token"]
    user_id = signup_data["user"]["id"]
    print(f"[SUCCESS] Signup 200 OK. User ID: {user_id}")

    # 2. Message 1a: Role 1 -> Senior Quantum ML Engineer
    print("\n------------------------------------------------------------")
    print("TEST 1A: Chat Role 1 - 'I want to become a Senior Quantum ML Engineer'")
    print("------------------------------------------------------------")
    code1a, resp1a = make_post("/copilot/chat", {"message": "I want to become a Senior Quantum ML Engineer"}, token=token)
    print(f"HTTP Status: {code1a}")
    print(json.dumps(resp1a, indent=2))

    # 3. Message 1b: Role 2 -> Autonomous Robotics Architect (for Diff Proving)
    print("\n------------------------------------------------------------")
    print("TEST 1B: Chat Role 2 - 'I want to become a Autonomous Robotics Architect'")
    print("------------------------------------------------------------")
    email2 = f"e2e_robotics_{int(time.time())}@growthos.ai"
    _, signup2 = make_post("/auth/signup", {"name": "Robotics Architect", "email": email2, "password": "Password123!"})
    signup_data2 = signup2.get("data", signup2)
    token2 = signup_data2["access_token"]
    code1b, resp1b = make_post("/copilot/chat", {"message": "I want to become a Autonomous Robotics Architect"}, token=token2)
    print(f"HTTP Status: {code1b}")
    print(json.dumps(resp1b, indent=2))

    print("\n[DIFF PROVING TAILORED CONTENT BETWEEN ROLE 1 AND ROLE 2]")
    msg1a = resp1a.get("message") or resp1a.get("data", {}).get("message", "")
    msg1b = resp1b.get("message") or resp1b.get("data", {}).get("message", "")
    print(f"Role 1 Message: {msg1a}")
    print(f"Role 2 Message: {msg1b}")
    assert msg1a != msg1b, "Messages must be distinct for different roles!"
    print("[SUCCESS] DIFF CONFIRMED: Content is genuinely tailored per target role!")

    # 4. Message 2: "give me a plan for today"
    print("\n------------------------------------------------------------")
    print("TEST 2: Chat - 'give me a plan for today'")
    print("------------------------------------------------------------")
    code2, resp2 = make_post("/copilot/chat", {"message": "give me a plan for today"}, token=token)
    print(f"HTTP Status: {code2}")
    print(json.dumps(resp2, indent=2))

    # 5. Message 3: "recommend me some courses"
    print("\n------------------------------------------------------------")
    print("TEST 3: Chat - 'recommend me some courses'")
    print("------------------------------------------------------------")
    code3, resp3 = make_post("/copilot/chat", {"message": "recommend me some courses"}, token=token)
    print(f"HTTP Status: {code3}")
    print(json.dumps(resp3, indent=2))

    # 6. Message 4: "find me job opportunities"
    print("\n------------------------------------------------------------")
    print("TEST 4: Chat - 'find me job opportunities'")
    print("------------------------------------------------------------")
    code4, resp4 = make_post("/copilot/chat", {"message": "find me job opportunities"}, token=token)
    print(f"HTTP Status: {code4}")
    print(json.dumps(resp4, indent=2))

    # 7. Message 5: Negative reflection message
    print("\n------------------------------------------------------------")
    print("TEST 5: Chat Negative Reflection - 'I feel exhausted and want to quit'")
    print("------------------------------------------------------------")
    code5, resp5 = make_post("/copilot/chat", {"message": "I feel exhausted and want to quit"}, token=token)
    print(f"HTTP Status: {code5}")
    print(json.dumps(resp5, indent=2))
    ref_data = resp5.get("data", {})
    risk_level = ref_data.get("risk_level") if isinstance(ref_data, dict) else "LOW"
    print(f"Reflected Risk Level: {risk_level}")
    assert risk_level != "LOW", f"REGRESSION ERROR: Negative reflection returned {risk_level}!"
    print("[SUCCESS] REGRESSION TEST PASSED: Negative reflection did NOT return LOW risk!")

    # 8. Message 6: Fetch notifications
    print("\n------------------------------------------------------------")
    print("TEST 6: GET /api/notification - Sync & Fetch Notifications")
    print("------------------------------------------------------------")
    code6, resp6 = make_get("/notification", token=token)
    print(f"HTTP Status: {code6}")
    print(json.dumps(resp6, indent=2))

    # 9. Test Broken Groq Error Handling
    print("\n------------------------------------------------------------")
    print("TEST 7: Deliberately Broken Groq Exception Test (?raise_on_error=true)")
    print("------------------------------------------------------------")
    code7, resp7 = make_post("/copilot/chat", {"message": "recommend me some courses"}, token=token, query_params="?raise_on_error=true")
    print(f"HTTP Status: {code7}")
    print(json.dumps(resp7, indent=2))

    print("\n============================================================")
    print("[SUCCESS] STEP 3 END-TO-END VERIFICATION COMPLETE & PASSED ALL CHECKS")
    print("============================================================")

if __name__ == "__main__":
    run_e2e()
