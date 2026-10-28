"""Epic 5a: weather-aware daily site protocols."""
from __future__ import annotations

from typing import Dict, List

CONDITIONS = ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"]

ADVISORIES: Dict[str, Dict[str, object]] = {
    "Normal": {
        "icon": "☀️", "level": "Low", "headline": "Standard operations",
        "alerts": [
            ("Hold the daily toolbox talk", "Low", "Brief crews on today's lifts, excavation and work at height before starting."),
            ("Run pre-shift checks", "Low", "Inspect scaffolds, ladders, lifting gear and temporary electrics before use."),
        ],
        "concrete": "Pour and cure as planned. Keep surfaces damp for at least 7 days with OPC, or 10 days with blended cement (IS 456 cl. 13.5).",
        "electrical": "Daily visual check of cables and distribution boards. Test RCDs weekly.",
        "equipment": "Normal crane and hoist operations within rated capacity.",
        "checklist": ["Toolbox talk done", "PPE issued and checked", "Scaffold tags current", "First-aid kit stocked", "Housekeeping walk completed"],
    },
    "High Wind": {
        "icon": "💨", "level": "High", "headline": "Wind alert: lifting and work at height restricted",
        "alerts": [
            ("Suspend crane operations", "Critical", "Stop lifts when wind reaches the crane manufacturer's limit, typically around 30-35 km/h. Lower the hook and set the jib to weathervane."),
            ("Stop work on scaffolds and open edges", "High", "Wind loads on sheeted scaffolds and formwork can topple them. Keep workers off the top decks."),
            ("Secure loose material", "High", "Tie down sheets, bricks, formwork panels and bagged cement. Falling objects are the main risk."),
            ("Control dust and grit", "Medium", "Wear eye protection and dust masks. Wet down dry earthwork."),
        ],
        "concrete": "Avoid placing slabs: wind speeds up surface drying and causes plastic shrinkage cracks. If pouring is unavoidable, use windbreaks, fog spray and cover finished surfaces immediately.",
        "electrical": "Check overhead lines and temporary cables for sway or contact. Isolate damaged supply.",
        "equipment": "Ground tower crane loads, retract mobile crane booms and park machinery away from edges.",
        "checklist": ["Crane out of service and secured", "Scaffold sheeting inspected", "Loose materials tied down", "Exclusion zones set under open edges", "Workers briefed on shelter points"],
    },
    "Heavy Rain": {
        "icon": "🌧️", "level": "High", "headline": "Rain alert: electrical and excavation hazards",
        "alerts": [
            ("Isolate temporary electrics", "Critical", "Switch off and lock out power in wet areas. Keep joints off the ground and confirm RCD protection before restart."),
            ("Inspect excavations and trenches", "Critical", "Water weakens trench walls. Keep people out until a competent person re-inspects shoring and slopes."),
            ("Slippery surfaces and ladders", "High", "Add anti-slip treads, restrict ladder use, and suspend roof or deck work."),
            ("Protect stored cement and steel", "Medium", "Raise cement off the floor and cover it. Keep steel off wet soil to limit rust."),
        ],
        "concrete": "Do not place concrete in heavy rain. Cover fresh pours with tarpaulin, protect edges and drain ponding. Check surface for washout and re-finish if needed.",
        "electrical": "Treat all wet-area equipment as live. Use only IP-rated and RCD-protected tools; replace damaged cables.",
        "equipment": "Keep machinery off saturated ground to avoid bogging and overturning. Dewater pits before work restarts.",
        "checklist": ["Power isolated in wet areas", "Trenches re-inspected", "Pumps running on pits", "Cement and steel covered", "Access routes cleared and gritted"],
    },
    "Extreme Heat": {
        "icon": "🔥", "level": "High", "headline": "Heat alert: worker health and hot-weather concreting",
        "alerts": [
            ("Enforce heat illness controls", "Critical", "Provide shade and drinking water at all work areas. Use work-rest cycles and move heavy tasks to early morning."),
            ("Watch for heat stroke", "High", "Look for confusion, hot dry skin or collapse. Move the person to shade, cool them and call emergency services."),
            ("Hot metal and surfaces", "Medium", "Steel, formwork and scaffolding can burn skin. Provide gloves and avoid long contact."),
            ("Reduce fatigue risk", "Medium", "Shorten shifts on exposed decks and rotate crews doing physical work."),
        ],
        "concrete": "Follow hot-weather concreting practice (IS 7861 Part 1): pour early morning or evening, keep concrete temperature below about 35-38 C using chilled water or ice, shade aggregates, and start curing immediately. Cure for at least 10 days with continuous wet curing.",
        "electrical": "Heat raises cable and panel temperatures. Check for overloaded extension leads and keep panels shaded and ventilated.",
        "equipment": "Check hydraulic and engine coolant levels. Do not leave pressurised cylinders in direct sun.",
        "checklist": ["Water and ORS at each work area", "Shaded rest points set up", "Work-rest schedule posted", "Pour scheduled outside peak heat", "Curing crew and water supply confirmed"],
    },
}


def get_advisory(condition: str) -> Dict[str, object]:
    return ADVISORIES.get(condition, ADVISORIES["Normal"])


def advisory_summary(condition: str) -> str:
    """One-paragraph summary used to give the chatbot the current weather context."""
    adv = get_advisory(condition)
    alerts: List = adv["alerts"]  # type: ignore[assignment]
    titles = "; ".join(a[0] for a in alerts)
    return f"Weather condition: {condition}. {adv['headline']}. Active alerts: {titles}. Concrete: {adv['concrete']}"
