# KNOWN: not a trained model — this is a hardcoded weighted formula, NOT a sklearn estimator.
# There are no .pkl files, no joblib.load(), and no training pipeline for this predictor.
# The formula derives stress_score from hours_worked, mood, and energy using fixed weights.
# To replace with a real model: train a sklearn LogisticRegression or RandomForestClassifier
# on labelled burnout survey data, serialize with joblib.dump(), and load via ml/model_loader.py.
# See backend/ENV_CHECKLIST.md § "Known Gaps" for tracking.
class BurnoutPredictor:
    def predict_burnout_risk(self, mood_score: int, energy_level: int, hours_worked: float) -> dict:
        stress_score = (hours_worked / 10.0) + (5 - mood_score) + (5 - energy_level)
        risk_percent = min(100.0, round((stress_score / 15.0) * 100.0, 1))

        if risk_percent > 65.0:
            level = "high"
        elif risk_percent > 35.0:
            level = "medium"
        else:
            level = "low"

        return {
            "burnout_risk_score": risk_percent,
            "burnout_risk_level": level
        }

burnout_predictor = BurnoutPredictor()
