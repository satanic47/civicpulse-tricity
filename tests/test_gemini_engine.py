import pytest
from app.core.gemini_engine import GeminiCivicEngine

def test_engine_initialization():
    engine = GeminiCivicEngine(api_key=None)
    assert engine is not None

def test_punjabi_language_detection_and_classification():
    engine = GeminiCivicEngine(api_key=None)
    result = engine.analyze_grievance("ਸਾਡੇ ਸੈਕਟਰ 22 ਸ਼ਾਸਤਰੀ ਮਾਰਕੀਟ ਕੋਲ ਪਾਣੀ ਦੀ ਪਾਈਪ ਫਟ ਗਈ ਹੈ", channel="VOICE")
    assert result["language_detected"] == "Punjabi"
    assert result["category"] == "Water Supply & Sewage"
    assert "Public Health" in result["department"]
    assert result["urgency_score"] >= 7

def test_hindi_language_detection_and_classification():
    engine = GeminiCivicEngine(api_key=None)
    result = engine.analyze_grievance("सेक्टर 35 सी होटल स्ट्रिप के पीछे मुख्य सड़क पर बहुत बड़े गड्ढे हैं", channel="WHATSAPP")
    assert result["language_detected"] == "Hindi"
    assert result["category"] == "Roads & Traffic"
    assert "Engineering Department" in result["department"]

def test_critical_urgency_detection():
    engine = GeminiCivicEngine(api_key=None)
    result = engine.analyze_grievance("Dangling live electrical wires sparking outside primary school", channel="WEB")
    assert result["category"] == "Street Lighting & Power"
    assert result["urgency_score"] >= 9
    assert result["sentiment"] == "urgent"

def test_policy_recommendation_generation():
    engine = GeminiCivicEngine(api_key=None)
    sample_grievances = [
        {"urgency_score": 9, "summary": "Pipe leak"},
        {"urgency_score": 8, "summary": "Sewage overflow"}
    ]
    budget_info = {"population": 36000, "ward": 7}
    rec = engine.generate_policy_recommendation("Sector 22", "Water Supply & Sewage", sample_grievances, budget_info)
    assert "Sector 22" in rec["title"]
    assert rec["priority_score"] > 50
    assert rec["estimated_cost_inr"] > 0
    assert rec["urgency_level"] in ["CRITICAL", "HIGH", "MEDIUM"]
