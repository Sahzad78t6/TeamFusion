from fastapi import APIRouter, Depends
from app.services.skill_graph_service import skill_graph_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("")
async def get_skills(user_id: str = Depends(get_current_user_id)):
    skills = await skill_graph_service.get_user_skills(user_id)
    alignment = await skill_graph_service.calculate_skill_alignment(user_id)
    return {
        "skills": skills,
        "skill_alignment_percent": round(alignment * 100, 1)
    }
