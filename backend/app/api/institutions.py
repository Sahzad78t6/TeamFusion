from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user, require_roles
from app.schemas.institution import AssessmentCreate, AssessmentSubmission, CohortCreate, InstitutionCreate, MembershipUpdate
from app.services.institution_service import institution_service

router = APIRouter(prefix="/institutions", tags=["Institutions"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_institution(payload: InstitutionCreate, admin: dict = Depends(require_roles("PLATFORM_ADMIN"))):
    return await institution_service.create_institution(payload.model_dump())

@router.post("/cohorts", status_code=status.HTTP_201_CREATED)
async def create_cohort(payload: CohortCreate, admin: dict = Depends(require_roles("INSTITUTION_ADMIN", "PLATFORM_ADMIN"))):
    return await institution_service.create_cohort(admin, payload.model_dump())

@router.get("/cohorts")
async def list_cohorts(admin: dict = Depends(require_roles("INSTITUTION_ADMIN", "PLATFORM_ADMIN"))):
    return await institution_service.list_cohorts(admin)

@router.put("/members")
async def assign_member(payload: MembershipUpdate, admin: dict = Depends(require_roles("INSTITUTION_ADMIN", "PLATFORM_ADMIN"))):
    await institution_service.assign_member(admin, payload.model_dump())
    return {"status": "updated"}

@router.get("/analytics")
async def get_institution_analytics(admin: dict = Depends(require_roles("INSTITUTION_ADMIN", "PLATFORM_ADMIN"))):
    return await institution_service.institution_analytics(admin)

@router.post("/assessments", status_code=status.HTTP_201_CREATED)
async def create_assessment(payload: AssessmentCreate, admin: dict = Depends(require_roles("INSTITUTION_ADMIN", "PLATFORM_ADMIN"))):
    return await institution_service.create_assessment(admin, payload.model_dump())

@router.get("/assessments")
async def list_assessments(student: dict = Depends(get_current_user)):
    return await institution_service.list_student_assessments(student)

@router.post("/assessments/{assessment_id}/submissions", status_code=status.HTTP_201_CREATED)
async def submit_assessment(assessment_id: str, payload: AssessmentSubmission, student: dict = Depends(get_current_user)):
    return await institution_service.submit_assessment(student, assessment_id, payload.answers)
