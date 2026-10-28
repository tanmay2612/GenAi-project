"""Tab 3: Planning and real estate valuation."""
from __future__ import annotations

import streamlit as st

from services import valuation_service as vs
from ui import components as c


def render(ctx) -> None:  # ctx unused here; kept for a uniform tab signature
    st.subheader("Planning and real estate valuation")
    st.caption("Estimate budget, spend to date, current asset value and material needs in INR. "
               "Rates are planning figures: replace them with local quotes before committing money.")

    a, b, d = st.columns([2, 3, 2])
    structure = a.selectbox("Structure type", list(vs.STRUCTURES), key="plan_structure")
    tier = b.selectbox("Location tier", list(vs.TIERS), index=1, key="plan_tier",
                       format_func=lambda t: str(vs.TIERS[t]["label"]))
    sqft = d.number_input("Built-up area (sq ft)", min_value=200, max_value=1_000_000, value=2400, step=100, key="plan_sqft")
    completion = st.slider("Completion (%)", 0, 100, 40, 5, key="plan_completion")

    try:
        v = vs.estimate(structure, float(sqft), int(tier), float(completion))
    except ValueError as exc:
        st.error(str(exc))
        return

    cols = st.columns(4)
    with cols[0]:
        c.metric_card("Total project budget", vs.format_inr(v.total_budget), f"{vs.format_inr(v.total_budget / sqft)} per sq ft", "info")
    with cols[1]:
        c.metric_card("Capex incurred", vs.format_inr(v.capex_incurred), f"{vs.format_inr(v.remaining_budget)} still to spend")
    with cols[2]:
        c.metric_card("Current asset value", vs.format_inr(v.current_asset_value), "Land plus built portion", "ok")
    with cols[3]:
        c.metric_card("Value on completion", vs.format_inr(v.full_market_value), "Estimated market value")

    st.write("")
    cols = st.columns(4)
    with cols[0]:
        c.metric_card("Steel required", f"{v.steel_total_tonnes:,.1f} t", f"{v.steel_used_tonnes:,.1f} t used so far")
    with cols[1]:
        c.metric_card("Cement required", f"{v.cement_total_bags:,.0f} bags", f"{v.cement_used_bags:,.0f} bags used so far")
    with cols[2]:
        c.metric_card("Steel remaining", f"{v.steel_total_tonnes - v.steel_used_tonnes:,.1f} t", "To procure")
    with cols[3]:
        c.metric_card("Cement remaining", f"{v.cement_total_bags - v.cement_used_bags:,.0f} bags", "To procure")

    left, right = st.columns([3, 2])
    with left:
        st.markdown("##### Budget breakdown")
        st.dataframe(
            [{"Head": k, "Amount": vs.format_inr(val), "Share": f"{val / v.total_budget:.0%}"} for k, val in v.budget_breakdown.items()],
            hide_index=True,
        )
    with right:
        st.markdown("##### Milestone progress")
        st.progress(completion / 100, text=f"{completion}% complete · {v.current_milestone}")
        for name, start, end in vs.MILESTONES:
            state = "done" if completion >= end else "active" if completion >= start and v.current_milestone == name else ""
            c.html_block(f'<div class="milestone {state}"><span class="dot"></span>{c.esc(name)}<small>{start}-{end}%</small></div>')

    c.download_json("Download valuation JSON", v.to_dict(), "planning_valuation.json", "plan_dl")

    st.divider()
    _render_concept(structure, int(tier), float(sqft), float(completion))
    c.disclaimer()


def _render_concept(structure: str, tier: int, sqft: float, completion: float) -> None:
    st.markdown("##### Conceptual 3D rendering")
    st.caption("Builds a prompt for Pollinations AI, which generates the image in your browser. "
               "It needs no key, and results are illustrative only.")
    style = st.selectbox("Architectural style", vs.STYLES, key="plan_style")
    default_prompt = vs.build_render_prompt(structure, tier, sqft, completion, style)
    prompt = st.text_area("Rendering prompt (edit to refine)", value=default_prompt, height=90,
                          key=f"plan_prompt_{hash(default_prompt)}")
    if st.button("Generate rendering", key="plan_render"):
        st.session_state["render_url"] = vs.pollinations_url(prompt)
    url = st.session_state.get("render_url")
    if url:
        st.image(url, caption="AI concept render (Pollinations)")
        st.markdown(f"[Open image in a new tab]({url})")
