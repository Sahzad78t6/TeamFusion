import numpy as np

class GrowthPredictor:
    def predict_growth_score(self, tasks_completed: int, total_hours: float, streak_days: int) -> float:
        # Base formula + non-linear weight scaling
        score = (tasks_completed * 1.5) + (total_hours * 1.2) + (streak_days * 2.0)
        return min(100.0, round(float(score), 1))

growth_predictor = GrowthPredictor()
