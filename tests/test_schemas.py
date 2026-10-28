import pytest

from core.schemas import extract_json, normalize_crack_report, normalize_safety_report, width_to_level


def test_extract_json_handles_code_fences_and_chatter():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Here you go: {"a": 2} hope that helps') == {"a": 2}


def test_extract_json_rejects_garbage():
    with pytest.raises(ValueError):
        extract_json("no json here")
    with pytest.raises(ValueError):
        extract_json("")


def test_safety_report_fills_missing_fields():
    report = normalize_safety_report({})
    assert [p["item"] for p in report["ppe_detection"]] == ["Helmet", "High-Vis Vest", "Safety Boots", "Safety Harness"]
    assert all(p["status"] == "Not Visible" for p in report["ppe_detection"])
    assert 0 <= report["safety_score"] <= 100


def test_safety_report_clamps_and_sorts():
    report = normalize_safety_report({
        "safety_score": 250,
        "ppe_detection": {"hard hat": "worn", "boots": "absent"},
        "hazards": [
            {"hazard": "a", "severity": "low"},
            {"hazard": "b", "severity": "critical"},
        ],
    })
    assert report["safety_score"] == 100
    assert report["ppe_detection"][0] == {"item": "Helmet", "status": "Detected", "notes": ""}
    assert report["ppe_detection"][2]["status"] == "Missing"
    assert [h["severity"] for h in report["hazards"]] == ["Critical", "Low"]


def test_overall_status_never_softer_than_score():
    assert normalize_safety_report({"safety_score": 30, "overall_status": "Compliant"})["overall_status"] == "Critical"
    assert normalize_safety_report({"safety_score": 95, "overall_status": "Needs Improvement"})["overall_status"] == "Needs Improvement"


@pytest.mark.parametrize("width,level", [(0.1, "Low"), (0.5, "Medium"), (1.5, "High"), (4.0, "Critical")])
def test_width_to_level(width, level):
    assert width_to_level(width) == level


def test_crack_report_upgrades_understated_severity():
    report = normalize_crack_report({"defect_type": "structural shear", "crack_width_mm": 5, "severity_level": "Low", "severity_score": 5})
    assert report["defect_type"] == "Structural Shear"
    assert report["severity_level"] == "Critical"
    assert report["severity_score"] >= 75


def test_crack_report_unknown_defect_and_repair_formats():
    report = normalize_crack_report({"defect_type": "weird", "recommended_repairs": ["Epoxy injection", {"method": "Grout", "description": "fill"}]})
    assert report["defect_type"] == "Unclassified"
    assert report["recommended_repairs"][0] == {"method": "Epoxy injection", "details": ""}
    assert report["recommended_repairs"][1]["details"] == "fill"
