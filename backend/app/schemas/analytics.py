from pydantic import BaseModel
from typing import List, Dict

class AnalyticsOverviewResponse(BaseModel):
    growth_score: float
    burnout_risk_score: float
    burnout_risk_level: str
    weekly_hours_logged: float
    tasks_completed_count: int
    streak_days: int
    skill_growth_trends: Dict[str, float]
