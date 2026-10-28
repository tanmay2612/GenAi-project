"""JSON data contracts: parsing and normalisation of model output.

Every report that reaches the UI passes through one of the ``normalize_*`` functions, so the
interface can rely on a fixed shape whether the data came from Gemini or from demo mode.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from core.config import (
    DEFECT_TYPES,
    PPE_ITEMS,
    SAFETY_STATUSES,
    SCHEMA_VERSION,
    SEVERITIES,
)

SEVERITY_RANK = {name: i for i, name in enumerate(SEVERITIES)}


# --------------------------------------------------------------------------- helpers
def extract_json(text: str) -> Dict[str, Any]:
    """Pull a JSON object out of a model response, tolerating code fences and chatter."""
    if not text or not text.strip():
        raise ValueError("The model returned an empty response.")
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("No JSON object found in the model response.")
    data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("Model response was JSON but not an object.")
    return data


def clamp_number(value: Any, lo: float, hi: float, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number != number:  # NaN
        return default
    return max(lo, min(hi, number))


def normalize_severity(value: Any, default: str = "Medium") -> str:
    text = str(value or "").strip().lower()
    for name in SEVERITIES:
        if text == name.lower():
            return name
    aliases = {
        "minor": "Low", "negligible": "Low", "moderate": "Medium",
        "major": "High", "severe": "High", "urgent": "Critical", "immediate": "Critical",
    }
    return aliases.get(text, default)


def _str_list(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def _more_severe(a: str, b: str) -> str:
    return a if SEVERITY_RANK[a] >= SEVERITY_RANK[b] else b


# --------------------------------------------------------------------------- safety
def status_from_score(score: float) -> str:
    if score >= 85:
        return "Compliant"
    if score >= 65:
        return "Needs Improvement"
    if score >= 40:
        return "Non-Compliant"
    return "Critical"


def _canonical_ppe(name: Any) -> str:
    text = str(name or "").lower()
    if "helmet" in text or "hard hat" in text or "hardhat" in text:
        return "Helmet"
    if "vest" in text or "hi-vis" in text or "high-vis" in text or "high vis" in text:
        return "High-Vis Vest"
    if "boot" in text or "shoe" in text or "footwear" in text:
        return "Safety Boots"
    if "harness" in text or "fall" in text:
        return "Safety Harness"
    return str(name or "Other PPE").strip().title()


def _ppe_status(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"detected", "present", "worn", "compliant", "yes", "true", "ok"}:
        return "Detected"
    if text in {"missing", "absent", "not worn", "no", "false", "non-compliant", "noncompliant"}:
        return "Missing"
    return "Not Visible"


def normalize_safety_report(raw: Dict[str, Any]) -> Dict[str, Any]:
    score = int(round(clamp_number(raw.get("safety_score"), 0, 100, 50)))

    entries = raw.get("ppe_detection") or []
    if isinstance(entries, dict):
        entries = [{"item": k, "status": v} for k, v in entries.items()]
    found: Dict[str, Dict[str, str]] = {}
    for entry in entries:
        if isinstance(entry, dict):
            item = _canonical_ppe(entry.get("item"))
            found[item] = {
                "item": item,
                "status": _ppe_status(entry.get("status")),
                "notes": str(entry.get("notes") or "").strip(),
            }
    ppe = [found.pop(name, {"item": name, "status": "Not Visible", "notes": ""}) for name in PPE_ITEMS]
    ppe.extend(found.values())  # any extra PPE the model reported (gloves, goggles, ...)

    hazards = []
    for h in raw.get("hazards") or raw.get("identified_hazards") or []:
        if isinstance(h, dict):
            hazards.append({
                "hazard": str(h.get("hazard") or h.get("description") or "Unspecified hazard").strip(),
                "severity": normalize_severity(h.get("severity")),
                "location": str(h.get("location") or "Site-wide").strip(),
                "remedy": str(h.get("remedy") or h.get("corrective_action") or "Consult the site safety officer.").strip(),
            })
    hazards.sort(key=lambda h: -SEVERITY_RANK[h["severity"]])

    # Take the more severe of the model's status and the score-derived status.
    derived = status_from_score(score)
    given = str(raw.get("overall_status") or "").strip()
    given = next((s for s in SAFETY_STATUSES if s.lower() == given.lower()), derived)
    status = max(given, derived, key=SAFETY_STATUSES.index)

    return {
        "report_type": "ppe_safety_audit",
        "schema_version": SCHEMA_VERSION,
        "safety_score": score,
        "overall_status": status,
        "workers_detected": int(clamp_number(raw.get("workers_detected"), 0, 500, 0)),
        "ppe_detection": ppe,
        "hazards": hazards,
        "summary": str(raw.get("summary") or "").strip(),
        "standards_referenced": _str_list(raw.get("standards_referenced"))
        or ["OSHA 29 CFR 1926", "BOCW Act 1996"],
    }


# --------------------------------------------------------------------------- cracks
def width_to_level(width_mm: float) -> str:
    """Severity implied by crack width alone (IS 456 cl. 35.3.2 uses 0.3 mm as the limit)."""
    if width_mm < 0.3:
        return "Low"
    if width_mm < 1.0:
        return "Medium"
    if width_mm < 3.0:
        return "High"
    return "Critical"


_SCORE_FLOOR = {"Low": 0, "Medium": 25, "High": 50, "Critical": 75}
_DEFAULT_URGENCY = {
    "Low": "Routine: monitor and re-inspect within 6 months",
    "Medium": "Plan repair within 1-3 months",
    "High": "Repair within 2 weeks; limit loading on the member",
    "Critical": "Immediate: restrict access and call a structural engineer",
}


def _match_defect(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "Unclassified"
    for name in DEFECT_TYPES:
        if text == name.lower() or name.lower() in text:
            return name
    return "Unclassified"


def normalize_crack_report(raw: Dict[str, Any]) -> Dict[str, Any]:
    width = round(clamp_number(raw.get("crack_width_mm"), 0.0, 50.0, 0.3), 2)
    level = _more_severe(normalize_severity(raw.get("severity_level")), width_to_level(width))
    score = int(round(clamp_number(raw.get("severity_score"), 0, 100, _SCORE_FLOOR[level] + 10)))
    score = max(score, _SCORE_FLOOR[level])

    repairs = []
    for item in raw.get("recommended_repairs") or []:
        if isinstance(item, dict):
            repairs.append({
                "method": str(item.get("method") or "Repair").strip(),
                "details": str(item.get("details") or item.get("description") or "").strip(),
            })
        elif str(item).strip():
            repairs.append({"method": str(item).strip(), "details": ""})

    return {
        "report_type": "crack_diagnostic",
        "schema_version": SCHEMA_VERSION,
        "defect_type": _match_defect(raw.get("defect_type")),
        "crack_width_mm": width,
        "crack_pattern": str(raw.get("crack_pattern") or "Not described").strip(),
        "severity_level": level,
        "severity_score": score,
        "urgency": str(raw.get("urgency") or _DEFAULT_URGENCY[level]).strip(),
        "root_causes": _str_list(raw.get("root_causes")),
        "recommended_repairs": repairs,
        "monitoring_plan": str(raw.get("monitoring_plan") or "").strip(),
        "confidence": round(clamp_number(raw.get("confidence"), 0, 1, 0.6), 2),
        "summary": str(raw.get("summary") or "").strip(),
    }
