import numpy as np

# KNOWN: not a trained model — this is a hardcoded weighted formula, NOT a sklearn estimator.
# There are no .pkl files, no joblib.load(), and no training pipeline for this predictor.
# The formula (tasks * 1.5 + hours * 1.2 + streak * 2.0) is a heuristic approximation.
# To replace with a real model: train a sklearn GradientBoostingRegressor or similar on
# historical learner data, serialize with joblib.dump(), and load via ml/model_loader.py.
# See backend/ENV_CHECKLIST.md § "Known Gaps" for tracking.
class GrowthPredictor:
    def predict_growth_score(self, tasks_completed: int, total_hours: float, streak_days: int) -> float:
        # Base formula + non-linear weight scaling
        score = (tasks_completed * 1.5) + (total_hours * 1.2) + (streak_days * 2.0)
        return min(100.0, round(float(score), 1))

growth_predictor = GrowthPredictor()
