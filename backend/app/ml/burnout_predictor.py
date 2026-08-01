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
