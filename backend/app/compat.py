import logging

logger = logging.getLogger(__name__)

def adapt_identity_to_planner(identity: dict) -> dict:
    target_role = identity.get("target_role") or identity.get("goal") or "AI Engineer"
    skills = identity.get("skills") or identity.get("key_strengths") or ["Python", "FastAPI"]
    goals = identity.get("goals") or identity.get("interests") or [f"Master {target_role}"]
    return {
        "target_role": target_role,
        "skills": skills,
        "goals": goals
    }

def adapt_identity_to_opportunity(identity: dict) -> dict:
    target_role = identity.get("target_role") or identity.get("goal") or "AI Developer"
    skills = identity.get("skills") or identity.get("key_strengths") or ["Python", "AI"]
    experience = identity.get("experience") or "Intermediate"
    goal = identity.get("goal") or target_role
    return {
        "target_role": target_role,
        "skills": skills,
        "experience": experience,
        "goal": goal
    }

def adapt_identity_to_learning_curator(identity: dict) -> dict:
    target_role = identity.get("target_role") or identity.get("goal") or "AI Specialist"
    skills = identity.get("skills") or identity.get("key_strengths") or ["Python", "FastAPI"]
    learning_style = identity.get("learning_style") or "Hands-on projects"
    return {
        "target_role": target_role,
        "skills": skills,
        "learning_style": learning_style
    }
