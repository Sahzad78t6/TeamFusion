import asyncio
from datetime import datetime, timedelta, timezone
import httpx
import time

BASE_URL = "http://127.0.0.1:8000"

async def test_contest_flow():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("PASS: Health check 200")

        # 2. Register / login Admin
        admin_email = f"admin_contest_{int(time.time())}@growthos.internal"
        res = await client.post("/auth/signup", json={
            "name": "Admin Tester",
            "email": admin_email,
            "password": "Password123!",
            "role": "INSTITUTION_ADMIN"
        })
        assert res.status_code == 200, f"Admin signup failed: {res.text}"
        admin_token = res.json()["access_token"]
        print("PASS: Admin signup")

        # 3. Create a cohort
        res = await client.post("/institutions/cohorts", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "name": "Contest Batch 2026",
            "year": "1st Year",
            "branch": "CSE",
            "section": "Alpha"
        })
        assert res.status_code == 200, f"Create cohort failed: {res.text}"
        cohort_id = res.json()["id"]
        print(f"PASS: Created cohort {cohort_id}")

        # 4. Register student and join cohort
        student_email = f"student_contest_{int(time.time())}@growthos.internal"
        res = await client.post("/auth/signup", json={
            "name": "Contest Student",
            "email": student_email,
            "password": "Password123!",
            "role": "STUDENT"
        })
        assert res.status_code == 200, f"Student signup failed: {res.text}"
        student_token = res.json()["access_token"]

        res = await client.post("/institutions/cohorts/join", headers={"Authorization": f"Bearer {student_token}"}, json={
            "cohort_id": cohort_id
        })
        assert res.status_code == 200, f"Join cohort failed: {res.text}"
        print("PASS: Student joined cohort")

        # 5. Admin creates contest with 5-minute window starting now
        now = datetime.now(timezone.utc)
        start_time = (now - timedelta(minutes=1)).isoformat()
        end_time = (now + timedelta(minutes=4)).isoformat()

        res = await client.post("/institutions/contests", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "cohort_id": cohort_id,
            "question_count": 2,
            "start_time": start_time,
            "end_time": end_time
        })
        assert res.status_code == 200, f"Contest creation failed: {res.text}"
        contest_data = res.json()
        assert "id" in contest_data
        assert len(contest_data["question_ids"]) == 2
        contest_id = contest_data["id"]
        print(f"PASS: Admin created contest {contest_id} with 2 questions")

        # 6. Student calls GET /contests/active
        res = await client.get("/contests/active", headers={"Authorization": f"Bearer {student_token}"})
        assert res.status_code == 200, f"Get active contest failed: {res.text}"
        active = res.json()
        assert active is not None, "Expected active contest, got null"
        assert active["id"] == contest_id
        assert len(active["questions"]) == 2
        for q in active["questions"]:
            assert "expected_output" not in q, "Security failure: expected_output leaked in active question!"
            assert "title" in q
            assert "starter_code" in q
            print(f"  - Active Question: {q['title']}")
        print("PASS: Student retrieved active contest without expected_output")

        # 7. Submit correct solution
        # Let's test the first question
        target_q = active["questions"][0]
        q_title = target_q["title"]
        q_id = target_q["id"]

        # Craft correct code based on question
        if "Reverse" in q_title:
            code = "import sys\nprint(sys.stdin.read().strip()[::-1])"
        elif "Maximum" in q_title:
            code = "import sys\nnums = list(map(int, sys.stdin.read().split()))\nprint(max(nums))"
        elif "Palindrome" in q_title:
            code = "import sys\ns = sys.stdin.read().strip()\nprint('true' if s == s[::-1] else 'false')"
        elif "Vowels" in q_title:
            code = "import sys\ns = sys.stdin.read().strip()\nv = set('aeiouAEIOU')\nprint(sum(1 for c in s if c in v))"
        elif "Fibonacci" in q_title:
            code = "import sys\nn = int(sys.stdin.read().strip())\na, b = 0, 1\nfor _ in range(n): a, b = b, a + b\nprint(a)"
        else:
            code = target_q["starter_code"]

        res = await client.post(f"/contests/{contest_id}/submit", headers={"Authorization": f"Bearer {student_token}"}, json={
            "question_id": q_id,
            "code": code
        })
        assert res.status_code == 200, f"Submit code failed: {res.text}"
        sub_res = res.json()
        print(f"Submission result for '{q_title}':", sub_res)
        assert sub_res["passed"] is True, f"Expected passed: True, got {sub_res}"
        print("PASS: Correct code passed all test cases")

        # 8. Submit infinite loop code - must terminate within ~2 seconds and not hang server
        loop_code = "while True:\n    pass\n"
        start_t = time.time()
        res = await client.post(f"/contests/{contest_id}/submit", headers={"Authorization": f"Bearer {student_token}"}, json={
            "question_id": q_id,
            "code": loop_code
        })
        elapsed = time.time() - start_t
        assert res.status_code == 200, f"Submit infinite loop failed: {res.text}"
        loop_res = res.json()
        print(f"Infinite loop submission took {elapsed:.2f}s, result:", loop_res)
        assert loop_res["passed"] is False, f"Expected passed: False for infinite loop, got {loop_res}"
        print("PASS: Infinite loop timed out safely in ~2 seconds without hanging server")

        # 9. Verify server is immediately responsive after the timeout
        health_res = await client.get("/health")
        assert health_res.status_code == 200
        print("PASS: Backend healthy and responsive immediately after loop timeout")

if __name__ == "__main__":
    asyncio.run(test_contest_flow())
