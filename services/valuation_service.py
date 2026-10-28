"""Epic 3: project planning, cost estimation and real estate valuation (INR).

All rates are illustrative planning figures, not market quotations. Edit the tables below to
match your city or contractor's rate card.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple
from urllib.parse import quote

# Construction cost per built-up sq ft (INR, Tier 2 baseline) plus material thumb rules.
STRUCTURES: Dict[str, Dict[str, float]] = {
    "Independent House (RCC)": {"cost": 1900, "steel_kg": 4.0, "cement_bags": 0.40, "market": 1.00},
    "Apartment / Residential Tower": {"cost": 2300, "steel_kg": 4.5, "cement_bags": 0.42, "market": 1.05},
    "Villa (Premium Finish)": {"cost": 3200, "steel_kg": 4.2, "cement_bags": 0.42, "market": 1.60},
    "Commercial Office Building": {"cost": 2800, "steel_kg": 5.0, "cement_bags": 0.45, "market": 1.50},
    "Industrial Warehouse (PEB)": {"cost": 1500, "steel_kg": 8.0, "cement_bags": 0.25, "market": 0.55},
}

TIERS: Dict[int, Dict[str, object]] = {
    1: {"label": "Tier 1 · Metro (Mumbai, Delhi NCR, Bengaluru, Hyderabad, Chennai, Kolkata, Pune)",
        "cost_multiplier": 1.25, "market_per_sqft": 11000},
    2: {"label": "Tier 2 · Large cities (Indore, Jaipur, Lucknow, Nagpur, Bhopal, Surat, Kochi)",
        "cost_multiplier": 1.00, "market_per_sqft": 6000},
    3: {"label": "Tier 3 · Smaller towns and district headquarters",
        "cost_multiplier": 0.85, "market_per_sqft": 3500},
}

BUDGET_SPLIT: Dict[str, float] = {
    "Foundation and RCC structure": 0.38,
    "Masonry, plaster and finishing": 0.27,
    "MEP (electrical, plumbing, HVAC)": 0.15,
    "Labour and site overheads": 0.12,
    "Professional fees and contingency": 0.08,
}

MILESTONES: List[Tuple[str, int, int]] = [
    ("Site preparation and foundation", 0, 15),
    ("Plinth and ground beams", 15, 25),
    ("RCC superstructure", 25, 55),
    ("Masonry and plastering", 55, 70),
    ("MEP rough-in", 70, 82),
    ("Flooring and finishing", 82, 95),
    ("Handover and snagging", 95, 100),
]

LAND_SHARE = 0.30       # share of finished market value that exists before any construction
CEMENT_BAG_KG = 50


@dataclass
class Valuation:
    structure_type: str
    tier: int
    built_up_sqft: float
    completion_pct: float
    total_budget: float
    capex_incurred: float
    remaining_budget: float
    full_market_value: float
    current_asset_value: float
    value_gain_vs_capex: float
    steel_total_tonnes: float
    steel_used_tonnes: float
    cement_total_bags: float
    cement_used_bags: float
    current_milestone: str
    budget_breakdown: Dict[str, float]

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["report_type"] = "planning_valuation"
        data["schema_version"] = "1.0"
        data["currency"] = "INR"
        return data


def estimate(structure_type: str, built_up_sqft: float, tier: int, completion_pct: float) -> Valuation:
    if structure_type not in STRUCTURES:
        raise ValueError(f"Unknown structure type: {structure_type}")
    if tier not in TIERS:
        raise ValueError(f"Unknown location tier: {tier}")
    if built_up_sqft <= 0:
        raise ValueError("Built-up area must be greater than zero.")
    completion = max(0.0, min(100.0, float(completion_pct))) / 100.0

    s, t = STRUCTURES[structure_type], TIERS[tier]
    budget = built_up_sqft * s["cost"] * float(t["cost_multiplier"])
    full_value = built_up_sqft * float(t["market_per_sqft"]) * s["market"]
    current_value = full_value * (LAND_SHARE + (1 - LAND_SHARE) * completion)
    capex = budget * completion

    steel_total = built_up_sqft * s["steel_kg"] / 1000
    cement_total = built_up_sqft * s["cement_bags"]

    return Valuation(
        structure_type=structure_type, tier=tier, built_up_sqft=built_up_sqft,
        completion_pct=completion * 100,
        total_budget=round(budget), capex_incurred=round(capex), remaining_budget=round(budget - capex),
        full_market_value=round(full_value), current_asset_value=round(current_value),
        value_gain_vs_capex=round(current_value - capex),
        steel_total_tonnes=round(steel_total, 2), steel_used_tonnes=round(steel_total * completion, 2),
        cement_total_bags=round(cement_total), cement_used_bags=round(cement_total * completion),
        current_milestone=milestone_for(completion * 100),
        budget_breakdown={k: round(budget * share) for k, share in BUDGET_SPLIT.items()},
    )


def milestone_for(pct: float) -> str:
    for name, _start, end in MILESTONES:
        if pct < end:
            return name
    return MILESTONES[-1][0]


def format_inr(amount: float) -> str:
    amount = float(amount)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    if amount >= 1e7:
        return f"{sign}₹{amount / 1e7:,.2f} Cr"
    if amount >= 1e5:
        return f"{sign}₹{amount / 1e5:,.2f} Lakhs"
    return f"{sign}₹{amount:,.0f}"


# ----------------------------------------------------------------- 3D concept rendering
STYLES = ["Contemporary Indian", "Modern minimalist", "Traditional Indian", "Industrial modern"]


def _stage_phrase(pct: float) -> str:
    if pct < 25:
        return "foundation and column starters under construction, rebar, excavators and scaffolding"
    if pct < 60:
        return "RCC frame under construction with brick masonry in progress and tower crane"
    if pct < 90:
        return "plastered facade with windows being fitted and light scaffolding"
    return "fully finished building with landscaping and warm lighting"


def build_render_prompt(structure_type: str, tier: int, sqft: float, completion_pct: float, style: str) -> str:
    place = {1: "metro city", 2: "mid-sized Indian city", 3: "small Indian town"}[tier]
    return (
        f"3D architectural rendering of a {structure_type.split('(')[0].strip().lower()} of about "
        f"{int(sqft):,} sq ft in a {place} in India, {style.lower()} design, "
        f"{_stage_phrase(completion_pct)}, golden hour light, photorealistic, wide angle, high detail"
    )


def pollinations_url(prompt: str, width: int = 1024, height: int = 640) -> str:
    seed = int(hashlib.sha256(prompt.encode()).hexdigest()[:6], 16)
    return (f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            f"?width={width}&height={height}&nologo=true&seed={seed}")
