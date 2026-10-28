import pytest

from services import valuation_service as vs


def test_budget_and_capex():
    v = vs.estimate("Independent House (RCC)", 1000, 2, 50)
    assert v.total_budget == 1_900_000
    assert v.capex_incurred == 950_000
    assert v.remaining_budget == 950_000


def test_asset_value_runs_from_land_share_to_full_value():
    start = vs.estimate("Independent House (RCC)", 1000, 2, 0)
    end = vs.estimate("Independent House (RCC)", 1000, 2, 100)
    assert end.current_asset_value == end.full_market_value == 6_000_000
    assert start.current_asset_value == 1_800_000


def test_tier_ordering():
    values = [vs.estimate("Villa (Premium Finish)", 2000, t, 60).total_budget for t in (3, 2, 1)]
    assert values == sorted(values)


def test_materials_scale_with_completion():
    v = vs.estimate("Apartment / Residential Tower", 2000, 1, 50)
    assert v.steel_used_tonnes == pytest.approx(v.steel_total_tonnes / 2, abs=0.01)
    assert v.cement_used_bags == pytest.approx(v.cement_total_bags / 2, abs=1)


def test_breakdown_sums_to_budget():
    v = vs.estimate("Commercial Office Building", 5000, 1, 10)
    assert abs(sum(v.budget_breakdown.values()) - v.total_budget) <= len(v.budget_breakdown)


def test_milestones():
    assert vs.milestone_for(0) == "Site preparation and foundation"
    assert vs.milestone_for(40) == "RCC superstructure"
    assert vs.milestone_for(100) == "Handover and snagging"


def test_format_inr():
    assert vs.format_inr(4_500_000) == "₹45.00 Lakhs"
    assert vs.format_inr(25_000_000) == "₹2.50 Cr"
    assert vs.format_inr(9_500) == "₹9,500"


def test_invalid_inputs():
    with pytest.raises(ValueError):
        vs.estimate("Nope", 1000, 2, 10)
    with pytest.raises(ValueError):
        vs.estimate("Independent House (RCC)", 0, 2, 10)
    with pytest.raises(ValueError):
        vs.estimate("Independent House (RCC)", 1000, 9, 10)


def test_render_prompt_and_url():
    prompt = vs.build_render_prompt("Villa (Premium Finish)", 1, 3000, 30, "Modern minimalist")
    assert "villa" in prompt and "3,000" in prompt
    assert vs.pollinations_url(prompt).startswith("https://image.pollinations.ai/prompt/")
