"""Epic 2a: PPE safety vision and site hazard audit."""
from __future__ import annotations

from typing import Any, Dict

from PIL import Image

from core.gemini_client import GeminiClient
from core.schemas import normalize_safety_report
from services.analysis import AnalysisResult, run_analysis

PROMPT = """You are a certified construction safety officer working on Indian building sites.
Audit the attached site photograph for worker PPE compliance and site hazards against OSHA
29 CFR 1926, the Indian BOCW Act 1996, and good practice for concrete works under IS 456:2000.

Rules:
- Judge only what is visible. If an item cannot be assessed, use the status "Not Visible".
- Never invent workers or equipment. Count only workers you can actually see.
- Every hazard needs a severity (Low, Medium, High or Critical) and a concrete corrective remedy.
- safety_score is 0-100 where 100 means fully compliant.

Return ONLY one JSON object with exactly this shape:
{
  "safety_score": 0,
  "overall_status": "Compliant | Needs Improvement | Non-Compliant | Critical",
  "workers_detected": 0,
  "ppe_detection": [
    {"item": "Helmet", "status": "Detected | Missing | Not Visible", "notes": "short evidence"},
    {"item": "High-Vis Vest", "status": "Detected | Missing | Not Visible", "notes": ""},
    {"item": "Safety Boots", "status": "Detected | Missing | Not Visible", "notes": ""},
    {"item": "Safety Harness", "status": "Detected | Missing | Not Visible", "notes": ""}
  ],
  "hazards": [
    {"hazard": "what is wrong", "severity": "Low | Medium | High | Critical",
     "location": "where in the photo", "remedy": "what to do about it"}
  ],
  "summary": "two sentences for the site manager",
  "standards_referenced": ["OSHA 29 CFR 1926.501", "..."]
}"""

_DEMOS = [
    {
        "safety_score": 62, "overall_status": "Needs Improvement", "workers_detected": 4,
        "ppe_detection": [
            {"item": "Helmet", "status": "Detected", "notes": "All four workers wear helmets."},
            {"item": "High-Vis Vest", "status": "Detected", "notes": "Three of four wear vests."},
            {"item": "Safety Boots", "status": "Missing", "notes": "Two workers appear to be in open footwear."},
            {"item": "Safety Harness", "status": "Missing", "notes": "Worker at the slab edge has no harness."},
        ],
        "hazards": [
            {"hazard": "Work at slab edge without fall protection", "severity": "Critical",
             "location": "Upper deck, right side",
             "remedy": "Stop edge work until guardrails or a harness tied to an anchor point are in place (OSHA 1926.501)."},
            {"hazard": "Exposed rebar ends without caps", "severity": "High", "location": "Column starters, foreground",
             "remedy": "Fit mushroom caps or bend rebar over to prevent impalement."},
            {"hazard": "Loose material and debris in walkways", "severity": "Medium", "location": "Ground level",
             "remedy": "Clear a 1 m walkway and assign a housekeeping crew each shift."},
        ],
        "summary": "Head protection is good, but the missing harness at the slab edge is an immediate fall risk. Fix footwear and housekeeping before the next shift.",
        "standards_referenced": ["OSHA 29 CFR 1926.501", "OSHA 29 CFR 1926.25", "BOCW Act 1996"],
    },
    {
        "safety_score": 86, "overall_status": "Compliant", "workers_detected": 3,
        "ppe_detection": [
            {"item": "Helmet", "status": "Detected", "notes": "All workers wear helmets with chin straps."},
            {"item": "High-Vis Vest", "status": "Detected", "notes": "High-visibility vests worn by all."},
            {"item": "Safety Boots", "status": "Detected", "notes": "Safety footwear visible on all workers."},
            {"item": "Safety Harness", "status": "Not Visible", "notes": "No work at height in view."},
        ],
        "hazards": [
            {"hazard": "Scaffold inspection tag not visible", "severity": "Low", "location": "Left scaffold bay",
             "remedy": "Display a dated inspection tag at every scaffold access point."},
            {"hazard": "Cables lying across a walkway", "severity": "Medium", "location": "Centre foreground",
             "remedy": "Route cables overhead or use cable ramps."},
        ],
        "summary": "PPE discipline is strong. Close out the minor housekeeping and tagging gaps to hold this score.",
        "standards_referenced": ["OSHA 29 CFR 1926.451", "BOCW Act 1996"],
    },
    {
        "safety_score": 34, "overall_status": "Critical", "workers_detected": 3,
        "ppe_detection": [
            {"item": "Helmet", "status": "Missing", "notes": "Two of three workers bare-headed."},
            {"item": "High-Vis Vest", "status": "Missing", "notes": "No high-visibility clothing seen."},
            {"item": "Safety Boots", "status": "Detected", "notes": "Boots visible on one worker."},
            {"item": "Safety Harness", "status": "Missing", "notes": "Worker on the ladder top is unprotected."},
        ],
        "hazards": [
            {"hazard": "Unprotected excavation edge with workers nearby", "severity": "Critical",
             "location": "Trench, mid-ground",
             "remedy": "Barricade the edge, keep spoil at least 0.6 m back, and shore or slope the trench wall (OSHA 1926.651)."},
            {"hazard": "Overhead load handled with people underneath", "severity": "High", "location": "Crane swing area",
             "remedy": "Set an exclusion zone and use a banksman for all lifts."},
            {"hazard": "Temporary electrical cable on wet ground", "severity": "High", "location": "Left foreground",
             "remedy": "Lift cables off the ground, use RCD protection, and replace damaged insulation."},
        ],
        "summary": "Several workers lack basic PPE and an open trench has no edge protection. Stop work in this area until it is made safe.",
        "standards_referenced": ["OSHA 29 CFR 1926.651", "OSHA 29 CFR 1926.100", "BOCW Act 1996"],
    },
]


def demo_report(digest: str) -> Dict[str, Any]:
    return _DEMOS[int(digest[:8], 16) % len(_DEMOS)]


def analyze(client: GeminiClient, image: Image.Image, digest: str) -> AnalysisResult:
    return run_analysis(client, PROMPT, image, normalize_safety_report, lambda: demo_report(digest))
