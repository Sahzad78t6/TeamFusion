from fastapi import APIRouter, Depends, status

from app.auth import get_current_user, to_user_response
from app.db import get_db
from app.models import IdentityResponse, OnboardingRequest, UserResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def submit_onboarding(
    payload: OnboardingRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["_id"]
    college_val = payload.skills[0] if payload.skills and len(payload.skills) > 0 else ""

    update_fields = {
        "goal": payload.goal,
        "year": payload.current_role,
        "college": college_val,
        "onboarding_completed": True,
    }

    # Auto-assign cohort_id if available matching college, year, or existing cohort
    matching_cohort = None
    if college_val:
        matching_cohort = await db["cohorts"].find_one({"name": college_val})
    if not matching_cohort and payload.current_role:
        matching_cohort = await db["cohorts"].find_one({"year": payload.current_role})
    if not matching_cohort:
        matching_cohort = await db["cohorts"].find_one({})

    if matching_cohort:
        update_fields["cohort_id"] = str(matching_cohort["_id"])
        update_fields["institution_id"] = matching_cohort.get("institution_id")

    await db["users"].update_one(
        {"_id": user_id},
        {"$set": update_fields}
    )

    # Upsert user_progress doc
    await db["user_progress"].update_one(
        {"user_id": str(user_id)},
        {
            "$set": {
                "goal": payload.goal,
                "year": payload.current_role,
                "current_topic_index": 0,
                "completed_topics": [],
            }
        },
        upsert=True
    )

    updated_user = await db["users"].find_one({"_id": user_id})
    return to_user_response(updated_user)

@router.get("/identity", response_model=IdentityResponse, status_code=status.HTTP_200_OK)
async def get_identity(current_user: dict = Depends(get_current_user)):
    user_goal = current_user.get("goal")
    return IdentityResponse(
        goal=user_goal,
        year=current_user.get("year"),
        college=current_user.get("college"),
        target_role=user_goal,
    )
