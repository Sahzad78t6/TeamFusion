from datetime import datetime, timedelta, timezone
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.db import get_db
from app.models import (
    AssessmentCreateRequest,
    AssessmentSubmissionRequest,
    CohortCreateRequest,
    CohortResponse,
    InstitutionAnalyticsResponse,
    JoinCohortRequest,
)

router = APIRouter(tags=["institutions"])

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") not in ["INSTITUTION_ADMIN", "PLATFORM_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

async def ensure_institution_id(db, user: dict) -> str:
    inst_id = user.get("institution_id")
    if not inst_id:
        inst_id = f"inst_{str(user['_id'])[-6:]}"
        await db["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {"institution_id": inst_id}}
        )
        user["institution_id"] = inst_id
    return inst_id

@router.get("/analytics", response_model=InstitutionAnalyticsResponse)
async def get_analytics(
    current_user: dict = Depends(require_admin),
):
    db = get_db()
    inst_id = await ensure_institution_id(db, current_user)

    cohorts = await db["cohorts"].find({"institution_id": inst_id}, {"_id": 1}).to_list(1000)
    cohort_ids = [str(c["_id"]) for c in cohorts]
    cohort_count = len(cohorts)

    total_students = await db["users"].count_documents({
        "$or": [
            {"institution_id": inst_id, "role": "STUDENT"},
            {"cohort_id": {"$in": cohort_ids}},
        ]
    })

    assessment_docs = await db["assessments"].find(
        {"cohort_id": {"$in": cohort_ids}},
        {"_id": 1}
    ).to_list(2000)
    assessment_ids = [str(a["_id"]) for a in assessment_docs]

    assessment_submissions = await db["submissions"].count_documents({
        "assessment_id": {"$in": assessment_ids}
    })

    return InstitutionAnalyticsResponse(
        total_students=total_students,
        cohort_count=cohort_count,
        assessment_submissions=assessment_submissions,
    )

@router.get("/cohorts", response_model=List[CohortResponse])
async def get_cohorts(
    current_user: dict = Depends(require_admin),
):
    db = get_db()
    inst_id = await ensure_institution_id(db, current_user)

    cohorts = await db["cohorts"].find({"institution_id": inst_id}).to_list(500)
    return [
        CohortResponse(
            id=str(c["_id"]),
            institution_id=c.get("institution_id", inst_id),
            name=c.get("name", ""),
            year=c.get("year", ""),
            branch=c.get("branch", ""),
            section=c.get("section", ""),
        )
        for c in cohorts
    ]

@router.post("/cohorts", response_model=CohortResponse, status_code=status.HTTP_200_OK)
async def create_cohort(
    payload: CohortCreateRequest,
    current_user: dict = Depends(require_admin),
):
    db = get_db()
    inst_id = await ensure_institution_id(db, current_user)

    doc = {
        "institution_id": inst_id,
        "name": payload.name.strip(),
        "year": payload.year.strip(),
        "branch": payload.branch.strip(),
        "section": (payload.section or "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db["cohorts"].insert_one(doc)

    return CohortResponse(
        id=str(result.inserted_id),
        institution_id=inst_id,
        name=doc["name"],
        year=doc["year"],
        branch=doc["branch"],
        section=doc["section"],
    )

@router.post("/cohorts/join")
async def join_cohort(
    payload: JoinCohortRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    cohort_id_str = payload.cohort_id or payload.code
    if not cohort_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cohort ID or code is required",
        )

    cohort = None
    try:
        cohort = await db["cohorts"].find_one({"_id": ObjectId(cohort_id_str)})
    except Exception:
        pass

    if not cohort:
        cohort = await db["cohorts"].find_one({"name": cohort_id_str})

    if not cohort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cohort not found",
        )

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "cohort_id": str(cohort["_id"]),
                "institution_id": cohort.get("institution_id"),
            }
        }
    )

    return {
        "cohort_id": str(cohort["_id"]),
        "name": cohort["name"],
        "message": f"Successfully joined cohort {cohort['name']}",
    }

@router.post("/assessments")
async def create_assessment(
    payload: AssessmentCreateRequest,
    current_user: dict = Depends(require_admin),
):
    db = get_db()
    inst_id = await ensure_institution_id(db, current_user)

    question_ids = []

    # Mode B: Bank-based random sampling
    if payload.year and payload.topic_code and payload.question_count and payload.question_count > 0:
        available_count = await db["quiz_bank"].count_documents({
            "year": payload.year,
            "topic_code": payload.topic_code,
        })

        if available_count < payload.question_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested question_count ({payload.question_count}) exceeds available questions ({available_count}) in quiz_bank for year '{payload.year}' and topic '{payload.topic_code}'",
            )

        pipeline = [
            {"$match": {"year": payload.year, "topic_code": payload.topic_code}},
            {"$sample": {"size": payload.question_count}},
        ]
        sampled_docs = await db["quiz_bank"].aggregate(pipeline).to_list(payload.question_count)
        question_ids = [doc["_id"] for doc in sampled_docs]

    # Mode A: Manual question creation
    elif payload.questions:
        for q in payload.questions:
            q_doc = {
                "year": payload.year or "1st Year",
                "topic_code": payload.topic_code or payload.skill.lower().replace(" ", "_"),
                "prompt": q.prompt,
                "options": q.options,
                "correct_option": q.correct_option,
            }
            res = await db["quiz_bank"].insert_one(q_doc)
            question_ids.append(res.inserted_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either provide questions (Mode A) or year, topic_code, and question_count (Mode B)",
        )

    now = datetime.now(timezone.utc)
    start_time = now.isoformat()
    end_time = (now + timedelta(hours=1)).isoformat()
    created_at = now.isoformat()

    assessment_doc = {
        "title": payload.title,
        "description": payload.description or "",
        "cohort_id": payload.cohort_id,
        "skill": payload.skill,
        "year": payload.year,
        "topic_code": payload.topic_code,
        "question_ids": question_ids,
        "start_time": start_time,
        "end_time": end_time,
        "created_at": created_at,
    }

    res = await db["assessments"].insert_one(assessment_doc)

    return {
        "id": str(res.inserted_id),
        "title": assessment_doc["title"],
        "description": assessment_doc["description"],
        "cohort_id": assessment_doc["cohort_id"],
        "skill": assessment_doc["skill"],
        "question_ids": [str(qid) for qid in question_ids],
        "start_time": start_time,
        "end_time": end_time,
        "created_at": created_at,
    }

@router.get("/assessments")
async def get_assessments(
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    cohort_id = current_user.get("cohort_id")

    # If student has no cohort yet, try to auto-match first cohort of matching year
    if not cohort_id:
        user_year = current_user.get("year") or "1st Year"
        matching_cohort = await db["cohorts"].find_one({"year": user_year})
        if matching_cohort:
            cohort_id = str(matching_cohort["_id"])
            await db["users"].update_one(
                {"_id": current_user["_id"]},
                {
                    "$set": {
                        "cohort_id": cohort_id,
                        "institution_id": matching_cohort.get("institution_id"),
                    }
                }
            )

    if not cohort_id:
        return []

    now_dt = datetime.now(timezone.utc)

    # Fetch assessments assigned to this cohort
    assessments_cursor = db["assessments"].find({"cohort_id": cohort_id})
    assessments_list = await assessments_cursor.to_list(100)

    result = []
    for a in assessments_list:
        # Check start_time <= now <= end_time
        try:
            st = datetime.fromisoformat(a["start_time"].replace("Z", "+00:00"))
            et = datetime.fromisoformat(a["end_time"].replace("Z", "+00:00"))
            if not (st <= now_dt <= et):
                continue
        except Exception:
            pass

        # Resolve questions from quiz_bank
        q_ids = a.get("question_ids", [])
        raw_questions = await db["quiz_bank"].find({"_id": {"$in": q_ids}}).to_list(len(q_ids))

        # IMPORTANT: Never include correct_option in this response
        resolved_questions = []
        for q in raw_questions:
            resolved_questions.append({
                "id": str(q["_id"]),
                "prompt": q["prompt"],
                "options": q["options"],
            })

        result.append({
            "id": str(a["_id"]),
            "title": a["title"],
            "description": a.get("description", ""),
            "skill": a.get("skill", ""),
            "questions": resolved_questions,
        })

    return result

@router.post("/assessments/{id}/submissions")
async def submit_assessment(
    id: str,
    payload: AssessmentSubmissionRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    try:
        assessment_obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment id",
        )

    assessment = await db["assessments"].find_one({"_id": assessment_obj_id})
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    q_ids = assessment.get("question_ids", [])
    questions = await db["quiz_bank"].find({"_id": {"$in": q_ids}}).to_list(len(q_ids))

    total_questions = len(questions)
    if total_questions == 0:
        score = 0.0
    else:
        correct_count = 0
        for q in questions:
            qid_str = str(q["_id"])
            if qid_str in payload.answers:
                if payload.answers[qid_str] == q.get("correct_option"):
                    correct_count += 1
        score = (correct_count / total_questions) * 100.0

    submission_doc = {
        "assessment_id": id,
        "user_id": str(current_user["_id"]),
        "answers": payload.answers,
        "score": round(score, 1),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }

    await db["submissions"].insert_one(submission_doc)

    return {"score": round(score, 1)}
