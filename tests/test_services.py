import hashlib

from PIL import Image

from core.gemini_client import GeminiClient
from services import chat_service, crack_service, safety_service, weather_service


def _img():
    return Image.new("RGB", (64, 64), "gray")


def _digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def test_safety_demo_mode_returns_valid_contract():
    result = safety_service.analyze(GeminiClient(""), _img(), _digest("a"))
    assert result.mode == "demo" and result.warning is None
    assert result.report["meta"]["mode"] == "demo"
    assert len(result.report["ppe_detection"]) >= 4


def test_crack_demo_mode_covers_every_template():
    seen = {crack_service.analyze(GeminiClient(""), _img(), _digest(str(i))).report["defect_type"] for i in range(40)}
    assert len(seen) >= 3 and "Unclassified" not in seen


def test_live_failure_falls_back_to_demo(monkeypatch):
    client = GeminiClient("fake-key")
    from core.gemini_client import GeminiError

    def boom(*a, **k):
        raise GeminiError("simulated outage")

    monkeypatch.setattr(client, "generate_json", boom)
    result = safety_service.analyze(client, _img(), _digest("x"))
    assert result.mode == "demo" and "simulated outage" in result.warning


def test_live_success_is_normalised(monkeypatch):
    client = GeminiClient("fake-key")
    monkeypatch.setattr(client, "generate_json", lambda p, i=None: {"defect_type": "Spalling", "crack_width_mm": "1.2"})
    result = crack_service.analyze(client, _img(), _digest("y"))
    assert result.mode == "live" and result.report["defect_type"] == "Spalling"
    assert result.report["severity_level"] == "High"


def test_every_weather_condition_has_full_advisory():
    for name in weather_service.CONDITIONS:
        adv = weather_service.get_advisory(name)
        assert adv["alerts"] and adv["concrete"] and adv["checklist"]
    assert "crane" in str(weather_service.get_advisory("High Wind")["alerts"]).lower()


def test_chat_demo_answers_and_fallback():
    client = GeminiClient("")
    reply, mode = chat_service.respond(client, [], "How long should I cure the slab?", "Normal")
    assert mode == "demo" and "IS 456" in reply
    reply, _ = chat_service.respond(client, [], "tell me a joke", "Normal")
    assert "demonstration mode" in reply
    reply, _ = chat_service.respond(client, [], "curing advice", "Extreme Heat")
    assert "Extreme Heat" in reply
