from typing import Literal
from pydantic import BaseModel, Field

class InstitutionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    type: str = Field(default="university", max_length=60)
    domain: str | None = Field(default=None, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    admin_user_id: str | None = None

class CohortCreate(BaseModel):
    institution_id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    year: str = Field(min_length=1, max_length=40)
    branch: str = Field(min_length=1, max_length=80)
    section: str | None = Field(default=None, max_length=40)

class MembershipUpdate(BaseModel):
    institution_id: str | None = None
    user_id: str
    cohort_id: str | None = None
    role: Literal["STUDENT", "INSTITUTION_ADMIN"] = "STUDENT"

class AssessmentQuestion(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=1000)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_option: int = Field(ge=0)
    skill: str = Field(min_length=1, max_length=100)

class AssessmentCreate(BaseModel):
    institution_id: str | None = None
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=2000)
    cohort_id: str
    skill: str = Field(min_length=1, max_length=100)
    questions: list[AssessmentQuestion] = Field(min_length=1, max_length=100)

class AssessmentSubmission(BaseModel):
    answers: dict[str, int]
