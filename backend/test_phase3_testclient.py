import time
from fastapi.testclient import TestClient
from pymongo import MongoClient
from bson import ObjectId

from app.main import app

def run_suite():
    with TestClient(app) as client:
        uid = int(time.time() * 1000)

        # 1. Sign up Institution Admin
        admin_payload = {
            "name": f"Admin User {uid}",
            "email": f"admin_{uid}@growthos.io",
            "password": "Password123!",
            "role": "INSTITUTION_ADMIN"
        }
        r_admin = client.post("/auth/signup", json=admin_payload)
        assert r_admin.status_code == 200, f"Admin signup failed: {r_admin.text}"
        admin_token = r_admin.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("1. [PASS] Admin registered with token.")

        # 2. Create Cohort as Admin
        cohort_payload = {
            "name": f"CSE Cohort {uid}",
            "year": "1st Year",
            "branch": "Computer Science & Engineering",
            "section": "A"
        }
        r_cohort = client.post("/institutions/cohorts", json=cohort_payload, headers=admin_headers)
        assert r_cohort.status_code == 200, f"Create cohort failed: {r_cohort.text}"
        cohort_data = r_cohort.json()
        cohort_id = cohort_data["id"]
        assert cohort_data["name"] == cohort_payload["name"]
        print(f"2. [PASS] Cohort created successfully (ID: {cohort_id}).")

        # 3. Mode B Error Handling: Request more questions than available in quiz_bank
        r_mode_b_overflow = client.post("/institutions/assessments", json={
            "title": "Overflow Quiz",
            "cohort_id": cohort_id,
            "skill": "DSA",
            "year": "1st Year",
            "topic_code": "dsa",
            "question_count": 999
        }, headers=admin_headers)
        assert r_mode_b_overflow.status_code == 400, "Should reject question_count exceeding pool"
        print("3. [PASS] Mode B boundary check rejected excess question_count properly.")

        # 4. Mode B Assessment Creation (Sample 5 DSA questions from quiz_bank)
        assessment_payload = {
            "title": f"DSA Foundational Benchmark {uid}",
            "description": "Comprehensive DSA test on arrays, lists, stacks, and queues",
            "cohort_id": cohort_id,
            "skill": "Data Structures & Algorithms",
            "year": "1st Year",
            "topic_code": "dsa",
            "question_count": 5
        }
        r_assess = client.post("/institutions/assessments", json=assessment_payload, headers=admin_headers)
        assert r_assess.status_code == 200, f"Assessment creation failed: {r_assess.text}"
        assess_data = r_assess.json()
        assessment_id = assess_data["id"]
        sampled_qids = assess_data["question_ids"]
        assert len(sampled_qids) == 5, f"Expected 5 questions, got {len(sampled_qids)}"
        print(f"4. [PASS] Assessment created via Mode B with 5 randomly sampled questions (ID: {assessment_id}).")

        # 5. Sign up Student assigned to this cohort
        student_payload = {
            "name": f"Student User {uid}",
            "email": f"student_{uid}@growthos.io",
            "password": "Password123!",
            "role": "STUDENT",
            "cohort_id": cohort_id
        }
        r_stud = client.post("/auth/signup", json=student_payload)
        assert r_stud.status_code == 200, f"Student signup failed: {r_stud.text}"
        student_token = r_stud.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        print(f"5. [PASS] Student registered and linked to cohort {cohort_id}.")

        # 6. Student views Assessments (GET /institutions/assessments)
        r_get_assess = client.get("/institutions/assessments", headers=student_headers)
        assert r_get_assess.status_code == 200, f"Get assessments failed: {r_get_assess.text}"
        assessments_list = r_get_assess.json()
        assert len(assessments_list) >= 1, "Student should receive at least 1 assessment"

        matched = next((a for a in assessments_list if a["id"] == assessment_id), None)
        assert matched is not None, "Target assessment not found in student's assessments list"
        assert len(matched["questions"]) == 5, f"Expected 5 questions in student view, got {len(matched['questions'])}"

        # Verify strict security: correct_option must NEVER be exposed
        for q in matched["questions"]:
            assert "prompt" in q and len(q["prompt"]) > 5
            assert "options" in q and len(q["options"]) == 4
            assert "id" in q
            assert "correct_option" not in q, f"SECURITY LEAK: correct_option found in student question: {q}"
        print("6. [PASS] Student assessment view verified — correct_option is strictly hidden.")

        # 7. Test Submissions: All Wrong Answers
        wrong_answers = {q["id"]: 99 for q in matched["questions"]}
        r_sub_wrong = client.post(f"/institutions/assessments/{assessment_id}/submissions", json={"answers": wrong_answers}, headers=student_headers)
        assert r_sub_wrong.status_code == 200, f"Submission failed: {r_sub_wrong.text}"
        score_wrong = r_sub_wrong.json()["score"]
        assert score_wrong == 0.0, f"Expected score 0.0 for all wrong, got {score_wrong}"
        print(f"7. [PASS] All-wrong submission graded accurately: score = {score_wrong}%.")

        # 8. Test Submissions: All Correct Answers
        from app.config import settings
        mongo = MongoClient(settings.MONGO_URI)
        db = mongo[settings.DB_NAME]
        db_questions = list(db["quiz_bank"].find({"_id": {"$in": [ObjectId(qid) for qid in sampled_qids]}}))
        assert len(db_questions) == 5, f"Expected 5 questions in db, got {len(db_questions)}"
        correct_answer_map = {str(doc["_id"]): doc["correct_option"] for doc in db_questions}
        print("   Sample question answers mapping:", correct_answer_map)

        r_sub_correct = client.post(f"/institutions/assessments/{assessment_id}/submissions", json={"answers": correct_answer_map}, headers=student_headers)
        assert r_sub_correct.status_code == 200, f"Submission failed: {r_sub_correct.text}"
        score_correct = r_sub_correct.json()["score"]
        assert score_correct == 100.0, f"Expected score 100.0 for all correct, got {score_correct}"
        print(f"8. [PASS] All-correct submission graded accurately: score = {score_correct}%.")

        # 9. Test Analytics as Admin
        r_analytics = client.get("/institutions/analytics", headers=admin_headers)
        assert r_analytics.status_code == 200, f"Analytics failed: {r_analytics.text}"
        analytics = r_analytics.json()
        print(f"9. [PASS] Institution Analytics: {analytics}")
        assert analytics["cohort_count"] >= 1
        assert analytics["total_students"] >= 1
        assert analytics["assessment_submissions"] >= 2

        # 10. Test Join Cohort endpoint
        r_join = client.post("/institutions/cohorts/join", json={"cohort_id": cohort_id}, headers=student_headers)
        assert r_join.status_code == 200, f"Join cohort failed: {r_join.text}"
        print(f"10. [PASS] Student join cohort verified: {r_join.json()['message']}")

        print("\n=== ALL 10 PHASE 3 VERIFICATION CHECKS PASSED WITH FLYING COLORS! ===")

if __name__ == "__main__":
    run_suite()
