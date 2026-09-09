import time
import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    email = f"phase2_tester_{uuid.uuid4().hex[:6]}@growthos.dev"
    print(f"Creating test student: {email}", flush=True)

    # 1. Signup
    r_signup = requests.post(f"{BASE_URL}/auth/signup", json={
        "name": "Phase2 Student",
        "email": email,
        "password": "Password123!"
    })
    assert r_signup.status_code == 200, f"Signup failed: {r_signup.text}"
    auth_data = r_signup.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Onboard
    r_onboard = requests.post(f"{BASE_URL}/onboarding", json={
        "goal": "ml_engineer",
        "current_role": "1st Year",
        "skills": ["National Institute of Tech"]
    }, headers=headers)
    assert r_onboard.status_code == 200, f"Onboarding failed: {r_onboard.text}"

    # Verification 1: GET /recommendation for fully-onboarded user -> confirm resources returned for "c_programming"
    r_rec1 = requests.get(f"{BASE_URL}/recommendation", headers=headers)
    assert r_rec1.status_code == 200, f"Expected 200, got {r_rec1.status_code}"
    rec1 = r_rec1.json()
    resources1 = rec1.get("resources", [])
    print(f"Initial topic: {rec1.get('current_topic')}, resources count: {len(resources1)}", flush=True)
    assert len(resources1) >= 3, f"Expected at least 3-4 resources, got {len(resources1)}"
    assert any("c_programming" in r.get("tags", []) or "c_programming" in r.get("id", "") for r in resources1), "Expected resources tagged with c_programming"
    print("Verification 1 PASS: Resources for c_programming successfully returned.", flush=True)

    # Check /dashboard and /planner before advancing
    r_dash1 = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    assert r_dash1.status_code == 200
    dash1 = r_dash1.json()
    assert dash1.get("current_topic") == "C Programming Fundamentals"
    assert dash1.get("progress_percent") == 0
    print(f"Dashboard verified: current_topic={dash1.get('current_topic')}, progress={dash1.get('progress_percent')}%", flush=True)

    r_planner1 = requests.get(f"{BASE_URL}/planner", headers=headers)
    assert r_planner1.status_code == 200
    planner1 = r_planner1.json()
    assert len(planner1) == 1
    assert planner1[0]["id"] == "c_programming"
    print(f"Planner verified: task={planner1[0]['title']}", flush=True)

    # Verification 2: PATCH /planner/tasks/c_programming {completed:true} -> GET /recommendation again -> confirm it now returns "python" resources
    r_patch1 = requests.patch(f"{BASE_URL}/planner/tasks/c_programming", json={"completed": True}, headers=headers)
    assert r_patch1.status_code == 200, f"Expected 200, got {r_patch1.status_code}"
    patch_res = r_patch1.json()
    assert patch_res.get("completed") is True

    r_rec2 = requests.get(f"{BASE_URL}/recommendation", headers=headers)
    assert r_rec2.status_code == 200
    rec2 = r_rec2.json()
    resources2 = rec2.get("resources", [])
    print(f"Advanced topic: {rec2.get('current_topic')}, resources count: {len(resources2)}", flush=True)
    assert any("python" in r.get("tags", []) or "python" in r.get("id", "") for r in resources2), "Expected resources tagged with python"
    print("Verification 2 PASS: Advanced to python and returned python resources.", flush=True)

    # Check dashboard progress after 1st task
    r_dash2 = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    assert r_dash2.status_code == 200
    dash2 = r_dash2.json()
    assert dash2.get("progress_percent") == 25
    print(f"Dashboard progress updated: {dash2.get('progress_percent')}%", flush=True)

    # Verification 3: Repeat step 2 until current_topic_index passes the last topic -> confirm {completed: true} is returned cleanly, no crash
    # Next topic: dsa
    requests.patch(f"{BASE_URL}/planner/tasks/python", json={"completed": True}, headers=headers)
    r_rec3 = requests.get(f"{BASE_URL}/recommendation", headers=headers)
    rec3 = r_rec3.json()
    assert rec3.get("current_topic") == "Data Structures & Algorithms"
    print(f"Topic 3: {rec3.get('current_topic')}", flush=True)

    # Next topic: communication
    requests.patch(f"{BASE_URL}/planner/tasks/dsa", json={"completed": True}, headers=headers)
    r_rec4 = requests.get(f"{BASE_URL}/recommendation", headers=headers)
    rec4 = r_rec4.json()
    assert rec4.get("current_topic") == "Technical Communication"
    print(f"Topic 4: {rec4.get('current_topic')}", flush=True)

    # Complete last topic (communication)
    requests.patch(f"{BASE_URL}/planner/tasks/communication", json={"completed": True}, headers=headers)
    r_rec_final = requests.get(f"{BASE_URL}/recommendation", headers=headers)
    assert r_rec_final.status_code == 200
    rec_final = r_rec_final.json()
    assert rec_final.get("completed") is True
    assert rec_final.get("resources") == []
    print(f"Final state: completed={rec_final.get('completed')}, resources={rec_final.get('resources')}", flush=True)

    r_dash_final = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    assert r_dash_final.status_code == 200
    dash_final = r_dash_final.json()
    assert dash_final.get("progress_percent") == 100
    print(f"Final Dashboard progress: {dash_final.get('progress_percent')}%", flush=True)

    r_planner_final = requests.get(f"{BASE_URL}/planner", headers=headers)
    assert r_planner_final.status_code == 200
    planner_final = r_planner_final.json()
    assert planner_final == []
    print("Final Planner tasks: [] (cleanly completed)", flush=True)

    print("Verification 3 PASS: Passed last topic and cleanly returned completed=True with no crash.", flush=True)

if __name__ == "__main__":
    run_tests()
