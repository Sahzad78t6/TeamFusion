"""Tenant-scoped institution, cohort, assessment, and analytics operations."""
from fastapi import HTTPException
from app.config.constants import COLLECTION_ASSESSMENTS, COLLECTION_ASSESSMENT_SUBMISSIONS, COLLECTION_COHORTS, COLLECTION_INSTITUTIONS, COLLECTION_USERS
from app.database.collections import get_collection, get_mock_collection
from app.database.repositories.user_repository import user_repository
from app.utils.helpers import generate_uuid, get_utc_now

class InstitutionService:
    async def _find_one(self, name: str, query: dict) -> dict | None:
        collection = get_collection(name)
        if collection is not None:
            return await collection.find_one(query)
        return next((item for item in get_mock_collection(name) if all(item.get(k) == v for k, v in query.items())), None)

    async def _insert(self, name: str, document: dict) -> dict:
        collection = get_collection(name)
        if collection is not None:
            await collection.insert_one(document)
        else:
            get_mock_collection(name).append(document)
        return document

    async def _list(self, name: str, query: dict) -> list[dict]:
        collection = get_collection(name)
        if collection is not None:
            return await collection.find(query, {"_id": 0}).to_list(length=1000)
        return [item for item in get_mock_collection(name) if all(item.get(k) == v for k, v in query.items())]

    async def create_institution(self, data: dict) -> dict:
        document = {"id": generate_uuid(), **data, "status": "active", "created_at": get_utc_now()}
        await self._insert(COLLECTION_INSTITUTIONS, document)
        if data.get("admin_user_id"):
            if not await user_repository.update_tenant_membership(data["admin_user_id"], document["id"], None, "INSTITUTION_ADMIN"):
                raise HTTPException(status_code=404, detail="Admin user was not found.")
        return document

    async def ensure_admin_scope(self, admin: dict, institution_id: str) -> None:
        if admin.get("role") == "PLATFORM_ADMIN":
            return
        if admin.get("role") != "INSTITUTION_ADMIN" or admin.get("institution_id") != institution_id:
            raise HTTPException(status_code=403, detail="Institution scope violation.")

    async def create_cohort(self, admin: dict, data: dict) -> dict:
        institution_id = admin.get("institution_id") or (data.get("institution_id") if admin.get("role") == "PLATFORM_ADMIN" else None)
        if not institution_id:
            raise HTTPException(status_code=400, detail="Administrator is not assigned to an institution.")
        if not await self._find_one(COLLECTION_INSTITUTIONS, {"id": institution_id}):
            raise HTTPException(status_code=404, detail="Institution was not found.")
        document = {"id": generate_uuid(), "institution_id": institution_id, **{k: v for k, v in data.items() if k != "institution_id"}, "created_at": get_utc_now()}
        return await self._insert(COLLECTION_COHORTS, document)

    async def assign_member(self, admin: dict, data: dict) -> None:
        institution_id = admin.get("institution_id") or (data.get("institution_id") if admin.get("role") == "PLATFORM_ADMIN" else None)
        if not institution_id:
            raise HTTPException(status_code=400, detail="Administrator is not assigned to an institution.")
        if data.get("cohort_id"):
            cohort = await self._find_one(COLLECTION_COHORTS, {"id": data["cohort_id"], "institution_id": institution_id})
            if not cohort:
                raise HTTPException(status_code=404, detail="Cohort was not found in your institution.")
        if not await user_repository.update_tenant_membership(data["user_id"], institution_id, data.get("cohort_id"), data.get("role")):
            raise HTTPException(status_code=404, detail="User was not found.")

    async def list_cohorts(self, admin: dict) -> list[dict]:
        institution_id = admin.get("institution_id")
        if not institution_id:
            raise HTTPException(status_code=400, detail="Administrator is not assigned to an institution.")
        return await self._list(COLLECTION_COHORTS, {"institution_id": institution_id})

    async def create_assessment(self, admin: dict, data: dict) -> dict:
        institution_id = admin.get("institution_id") or (data.get("institution_id") if admin.get("role") == "PLATFORM_ADMIN" else None)
        if not institution_id:
            raise HTTPException(status_code=400, detail="Administrator is not assigned to an institution.")
        cohort = await self._find_one(COLLECTION_COHORTS, {"id": data["cohort_id"], "institution_id": institution_id})
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort was not found in your institution.")
        document = {"id": generate_uuid(), "institution_id": institution_id, "creator_id": admin["id"], **{k: v for k, v in data.items() if k != "institution_id"}, "created_at": get_utc_now()}
        return await self._insert(COLLECTION_ASSESSMENTS, document)

    async def list_student_assessments(self, student: dict) -> list[dict]:
        if not student.get("institution_id") or not student.get("cohort_id"):
            return []
        assessments = await self._list(COLLECTION_ASSESSMENTS, {"institution_id": student["institution_id"], "cohort_id": student["cohort_id"]})
        # Correct answers must never be sent to students.
        return [
            {**assessment, "questions": [{key: value for key, value in question.items() if key != "correct_option"} for question in assessment["questions"]]}
            for assessment in assessments
        ]

    async def submit_assessment(self, student: dict, assessment_id: str, answers: dict[str, int]) -> dict:
        assessment = await self._find_one(COLLECTION_ASSESSMENTS, {"id": assessment_id, "institution_id": student.get("institution_id"), "cohort_id": student.get("cohort_id")})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment is unavailable for your cohort.")
        existing = await self._find_one(COLLECTION_ASSESSMENT_SUBMISSIONS, {"assessment_id": assessment_id, "student_id": student["id"]})
        if existing:
            raise HTTPException(status_code=409, detail="Assessment has already been submitted.")
        questions = assessment["questions"]
        correct = sum(answers.get(q["id"]) == q["correct_option"] for q in questions)
        score = round((correct / len(questions)) * 100, 2)
        submission = {"id": generate_uuid(), "assessment_id": assessment_id, "institution_id": student["institution_id"], "cohort_id": student["cohort_id"], "student_id": student["id"], "score": score, "correct_answers": correct, "question_count": len(questions), "submitted_at": get_utc_now()}
        await self._insert(COLLECTION_ASSESSMENT_SUBMISSIONS, submission)
        return submission

    async def institution_analytics(self, admin: dict) -> dict:
        institution_id = admin.get("institution_id")
        students = await self._list(COLLECTION_USERS, {"institution_id": institution_id, "role": "STUDENT"})
        cohorts = await self._list(COLLECTION_COHORTS, {"institution_id": institution_id})
        submissions = await self._list(COLLECTION_ASSESSMENT_SUBMISSIONS, {"institution_id": institution_id})
        by_cohort = []
        for cohort in cohorts:
            cohort_submissions = [s for s in submissions if s["cohort_id"] == cohort["id"]]
            scores = [s["score"] for s in cohort_submissions]
            by_cohort.append({"cohort_id": cohort["id"], "name": cohort["name"], "student_count": sum(s.get("cohort_id") == cohort["id"] for s in students), "assessment_submissions": len(scores), "average_score": round(sum(scores) / len(scores), 2) if scores else None})
        return {"institution_id": institution_id, "total_students": len(students), "cohort_count": len(cohorts), "assessment_submissions": len(submissions), "average_assessment_score": round(sum(s["score"] for s in submissions) / len(submissions), 2) if submissions else None, "cohorts": by_cohort}

institution_service = InstitutionService()
