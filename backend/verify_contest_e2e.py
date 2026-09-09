import asyncio
import httpx
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"

async def setup_e2e_contest():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        ts = int(datetime.now().timestamp())
        admin_email = f"contest_admin_{ts}@growthos.com"
        admin_pass = "AdminPass123!"
        student_email = f"contest_student_{ts}@growthos.com"
        student_pass = "StudentPass123!"

        # Admin signup
        res = await client.post("/auth/signup", json={
            "email": admin_email,
            "password": admin_pass,
            "name": "Contest Admin",
            "role": "INSTITUTION_ADMIN"
        })
        assert res.status_code == 200, res.text
        admin_token = res.json()["access_token"]

        # Admin creates cohort
        res = await client.post("/institutions/cohorts", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "name": "B.Tech CSE 2026",
            "year": "1st Year",
            "branch": "Computer Science",
            "section": "A"
        })
        assert res.status_code == 200, res.text
        cohort_id = res.json()["id"]

        # Student signup
        res = await client.post("/auth/signup", json={
            "email": student_email,
            "password": student_pass,
            "name": "Contest Student",
            "role": "STUDENT"
        })
        assert res.status_code == 200, res.text
        student_token = res.json()["access_token"]

        # Student joins cohort
        res = await client.post("/institutions/cohorts/join", headers={"Authorization": f"Bearer {student_token}"}, json={
            "cohort_id": cohort_id
        })
        assert res.status_code == 200, res.text

        # 1. curl POST /institutions/contests with a 5-minute window starting now
        now = datetime.now(timezone.utc)
        start_time = (now - timedelta(seconds=10)).isoformat()
        end_time = (now + timedelta(minutes=30)).isoformat()

        res = await client.post("/institutions/contests", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "cohort_id": cohort_id,
            "question_count": 2,
            "start_time": start_time,
            "end_time": end_time
        })
        assert res.status_code == 200, res.text
        contest = res.json()
        contest_id = contest["id"]
        print(f"PASS #1: POST /institutions/contests created contest {contest_id}")

        # Confirm GET /contests/active returns it
        res = await client.get("/contests/active", headers={"Authorization": f"Bearer {student_token}"})
        assert res.status_code == 200, res.text
        active = res.json()
        assert active is not None
        assert active["id"] == contest_id
        assert len(active["questions"]) == 2
        for q in active["questions"]:
            assert "expected_output" not in str(q)
        print("PASS #1: GET /contests/active returned active contest session without expected_output")

        print(f"\nSTUDENT_EMAIL={student_email}")
        print(f"STUDENT_PASSWORD={student_pass}")
        print(f"STUDENT_TOKEN={student_token}")
        print(f"CONTEST_ID={contest_id}")
        return {
            "student_email": student_email,
            "student_password": student_pass,
            "student_token": student_token,
            "contest_id": contest_id
        }

if __name__ == "__main__":
    asyncio.run(setup_e2e_contest())
