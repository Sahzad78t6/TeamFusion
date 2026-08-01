from app.ml.growth_predictor import growth_predictor
from app.ml.burnout_predictor import burnout_predictor

def test_growth_predictor():
    score = growth_predictor.predict_growth_score(tasks_completed=10, total_hours=20.0, streak_days=5)
    assert score > 0
    assert score <= 100.0

def test_burnout_predictor():
    res = burnout_predictor.predict_burnout_risk(mood_score=5, energy_level=5, hours_worked=15.0)
    assert "burnout_risk_score" in res
    assert "burnout_risk_level" in res
