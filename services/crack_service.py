"""Epic 2b: concrete crack classification and structural diagnostics."""
from __future__ import annotations

from typing import Any, Dict

from PIL import Image

from core.gemini_client import GeminiClient
from core.schemas import normalize_crack_report
from services.analysis import AnalysisResult, run_analysis

PROMPT = """You are a senior structural engineer specialising in concrete defect diagnosis in India.
Examine the attached photo of a concrete or masonry surface and classify the defect.

Classify defect_type as exactly one of: Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling.
Use these cues:
- Hairline: very fine, random or map-like cracks, usually shrinkage.
- Settlement: vertical or stepped cracks wider at one end, often near foundations or openings.
- Structural Shear: diagonal cracks about 45 degrees near supports or beam-column joints.
- Thermal Expansion: straight cracks at regular spacing in slabs, parapets or long walls.
- Spalling: concrete surface breaking away, often with exposed or corroded rebar.

Estimate crack_width_mm from visible scale cues (coins, rulers, bricks, joints). If there is no scale,
give your best estimate and lower the confidence. Use IS 456:2000 cl. 35.3.2 (0.3 mm general limit)
as the reference for acceptable width. severity_score is 0-100.

Return ONLY one JSON object with exactly this shape:
{
  "defect_type": "Hairline | Settlement | Structural Shear | Thermal Expansion | Spalling",
  "crack_width_mm": 0.0,
  "crack_pattern": "orientation, length and spread",
  "severity_level": "Low | Medium | High | Critical",
  "severity_score": 0,
  "urgency": "when action is needed",
  "root_causes": ["..."],
  "recommended_repairs": [{"method": "e.g. Epoxy injection", "details": "how and where"}],
  "monitoring_plan": "e.g. crack gauges, re-inspection interval",
  "confidence": 0.0,
  "summary": "two sentences for the site engineer"
}"""

_DEMOS = [
    {
        "defect_type": "Hairline", "crack_width_mm": 0.2, "crack_pattern": "Fine random map cracking across the plastered surface",
        "severity_level": "Low", "severity_score": 14, "urgency": "Routine: re-inspect within 6 months",
        "root_causes": ["Plastic shrinkage from rapid moisture loss", "Inadequate curing of plaster"],
        "recommended_repairs": [
            {"method": "Surface sealing", "details": "Brush a polymer-modified cement slurry into the cracks."},
            {"method": "Elastomeric coating", "details": "Apply a crack-bridging coat after the slurry has cured."}],
        "monitoring_plan": "Mark crack ends with a pencil and date; re-check after one monsoon season.",
        "confidence": 0.78, "summary": "Cosmetic shrinkage cracking within the 0.3 mm limit. Seal it to keep moisture out.",
    },
    {
        "defect_type": "Settlement", "crack_width_mm": 2.5, "crack_pattern": "Vertical, stepped crack through masonry, wider at the top",
        "severity_level": "High", "severity_score": 68, "urgency": "Repair within 2 weeks after confirming movement has stopped",
        "root_causes": ["Differential settlement of the footing", "Poor soil compaction or seasonal moisture change"],
        "recommended_repairs": [
            {"method": "Foundation assessment", "details": "Commission a geotechnical check and trial pit at the affected corner."},
            {"method": "Underpinning", "details": "Underpin the footing if movement is confirmed."},
            {"method": "Epoxy injection and re-grouting", "details": "Inject and re-grout the crack only after movement has stabilised."}],
        "monitoring_plan": "Fix tell-tale gauges across the crack and read them weekly for 8 weeks.",
        "confidence": 0.72, "summary": "Stepped cracking that widens upward points to differential settlement. Stabilise the foundation before repairing the wall.",
    },
    {
        "defect_type": "Structural Shear", "crack_width_mm": 4.5, "crack_pattern": "Diagonal crack at about 45 degrees near the beam support",
        "severity_level": "Critical", "severity_score": 88, "urgency": "Immediate: restrict access and call a structural engineer",
        "root_causes": ["Insufficient shear reinforcement or stirrup spacing", "Overloading beyond design capacity"],
        "recommended_repairs": [
            {"method": "Temporary propping", "details": "Prop the member and remove live load immediately."},
            {"method": "Structural strengthening", "details": "Jacket the beam or bond FRP wraps as designed by a structural engineer."},
            {"method": "Epoxy injection", "details": "Inject cracks once the strengthening scheme is approved."}],
        "monitoring_plan": "Install crack monitors and review daily until the strengthening is complete.",
        "confidence": 0.8, "summary": "A wide diagonal crack at a support is a classic shear failure sign. Treat the member as unsafe until it is propped and assessed.",
    },
    {
        "defect_type": "Spalling", "crack_width_mm": 1.5, "crack_pattern": "Concrete cover breaking away along a beam soffit with rust staining",
        "severity_level": "High", "severity_score": 60, "urgency": "Repair within 2 weeks to stop section loss",
        "root_causes": ["Rebar corrosion expanding behind the cover", "Low cover or high chloride or carbonation exposure"],
        "recommended_repairs": [
            {"method": "Break out and clean", "details": "Remove loose concrete and clean rebar to bright metal."},
            {"method": "Anti-corrosion treatment", "details": "Apply a zinc-rich or epoxy primer to the bars."},
            {"method": "Polymer-modified mortar repair", "details": "Reinstate the section and finish with a protective coating."}],
        "monitoring_plan": "Re-inspect the repaired area at 3 and 12 months; test cover depth with a cover meter.",
        "confidence": 0.75, "summary": "Corroding reinforcement is pushing off the cover. Repair now before the bar section reduces.",
    },
    {
        "defect_type": "Thermal Expansion", "crack_width_mm": 0.6, "crack_pattern": "Straight transverse cracks at regular spacing along a terrace slab",
        "severity_level": "Medium", "severity_score": 38, "urgency": "Plan repair within 1-3 months, before the next monsoon",
        "root_causes": ["Daily temperature cycling without expansion joints", "Missing or failed terrace insulation"],
        "recommended_repairs": [
            {"method": "Route and seal", "details": "Cut a V-groove along each crack and fill with a flexible polyurethane sealant."},
            {"method": "Expansion joints", "details": "Introduce joints at regular spacing in the screed."},
            {"method": "Reflective waterproofing", "details": "Apply a heat-reflective membrane over the slab."}],
        "monitoring_plan": "Check width in summer and winter; it should open and close seasonally.",
        "confidence": 0.7, "summary": "Evenly spaced straight cracks suggest thermal movement. Use flexible sealants, not rigid grout.",
    },
]


def demo_report(digest: str) -> Dict[str, Any]:
    return _DEMOS[int(digest[:8], 16) % len(_DEMOS)]


def analyze(client: GeminiClient, image: Image.Image, digest: str) -> AnalysisResult:
    return run_analysis(client, PROMPT, image, normalize_crack_report, lambda: demo_report(digest))
