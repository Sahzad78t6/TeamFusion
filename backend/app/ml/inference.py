from app.ml.growth_predictor import growth_predictor
from app.ml.burnout_predictor import burnout_predictor

class MLInferenceEngine:
    def run_full_analytics_inference(self, tasks_completed: int, total_hours: float, streak_days: int, mood_score: int, energy_level: int) -> dict:
        growth_score = growth_predictor.predict_growth_score(tasks_completed, total_hours, streak_days)
        burnout = burnout_predictor.predict_burnout_risk(mood_score, energy_level, total_hours)
        return {
            "growth_score": growth_score,
            **burnout
        }

ml_inference = MLInferenceEngine()
