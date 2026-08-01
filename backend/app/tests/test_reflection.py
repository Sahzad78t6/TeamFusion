import asyncio
from app.agents.reflection.agent import reflection_agent, extract_sentiment_scores
from app.agents.reflection.tools import compute_burnout_risk_indicator

def test_extract_sentiment_scores_negative():
    notes = "I feel stressed and burnt out and completely exhausted"
    mood, energy = extract_sentiment_scores(notes)
    assert mood <= 2, f"Expected mood <= 2, got {mood}"
    assert energy <= 2, f"Expected energy <= 2, got {energy}"
    risk = compute_burnout_risk_indicator(mood, energy, study_hours=2.5)
    assert risk != "LOW", f"Expected risk != LOW, got {risk}"
    assert risk in ("HIGH_RISK", "MODERATE"), f"Expected HIGH_RISK or MODERATE, got {risk}"
    print("[PASS] test_extract_sentiment_scores_negative")

def test_extract_sentiment_scores_positive():
    notes = "Feeling great, very energized and loving the productive day!"
    mood, energy = extract_sentiment_scores(notes)
    assert mood >= 4
    assert energy >= 4
    risk = compute_burnout_risk_indicator(mood, energy, study_hours=2.5)
    assert risk == "LOW"
    print("[PASS] test_extract_sentiment_scores_positive")

async def test_reflection_process_negative_notes_not_low_risk():
    user_id = "test_sentiment_user"
    notes = "I feel stressed and burnt out and overwhelmed"
    res = await reflection_agent.process_and_save(user_id, {"notes": notes})
    assert res["risk_level"] != "LOW", f"Expected risk != LOW, got {res['risk_level']}"
    assert res["mood_score"] <= 2, f"Expected mood_score <= 2, got {res['mood_score']}"
    print(f"[PASS] test_reflection_process_negative_notes_not_low_risk (risk_level={res['risk_level']})")

if __name__ == "__main__":
    test_extract_sentiment_scores_negative()
    test_extract_sentiment_scores_positive()
    asyncio.run(test_reflection_process_negative_notes_not_low_risk())
