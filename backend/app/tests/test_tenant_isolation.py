import pytest
from fastapi import HTTPException
from app.database.mongodb import mock_db_storage
from app.database.repositories.user_repository import user_repository
from app.services.institution_service import institution_service

@pytest.mark.asyncio
async def test_student_cannot_read_or_submit_another_institutions_assessment():
    mock_db_storage.clear()
    admin_a = await user_repository.create_user({"name": "Admin A", "email": "admin-a@example.test", "role": "INSTITUTION_ADMIN"})
    admin_b = await user_repository.create_user({"name": "Admin B", "email": "admin-b@example.test", "role": "INSTITUTION_ADMIN"})
    student_a = await user_repository.create_user({"name": "Student A", "email": "student-a@example.test"})
    student_b = await user_repository.create_user({"name": "Student B", "email": "student-b@example.test"})

    institution_a = await institution_service.create_institution({"name": "Institution A", "admin_user_id": admin_a["id"]})
    institution_b = await institution_service.create_institution({"name": "Institution B", "admin_user_id": admin_b["id"]})
    admin_a["institution_id"] = institution_a["id"]
    admin_b["institution_id"] = institution_b["id"]
    cohort_a = await institution_service.create_cohort(admin_a, {"name": "CSE A", "year": "2", "branch": "CSE", "section": "A"})
    cohort_b = await institution_service.create_cohort(admin_b, {"name": "ECE B", "year": "2", "branch": "ECE", "section": "B"})
    await institution_service.assign_member(admin_a, {"user_id": student_a["id"], "cohort_id": cohort_a["id"], "role": "STUDENT"})
    await institution_service.assign_member(admin_b, {"user_id": student_b["id"], "cohort_id": cohort_b["id"], "role": "STUDENT"})
    student_a = await user_repository.get_by_id(student_a["id"])
    student_b = await user_repository.get_by_id(student_b["id"])
    assessment = await institution_service.create_assessment(admin_a, {"title": "ML Assessment", "description": "", "cohort_id": cohort_a["id"], "skill": "Machine Learning", "questions": [{"id": "q1", "prompt": "2 + 2?", "options": ["3", "4"], "correct_option": 1, "skill": "Math"}]})

    assert [a["id"] for a in await institution_service.list_student_assessments(student_a)] == [assessment["id"]]
    assert await institution_service.list_student_assessments(student_b) == []
    with pytest.raises(HTTPException, match="unavailable"):
        await institution_service.submit_assessment(student_b, assessment["id"], {"q1": 1})
