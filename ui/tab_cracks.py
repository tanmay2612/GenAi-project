"""Tab 2: Crack diagnostics and structural integrity."""
from __future__ import annotations

import streamlit as st

from core.config import SUPPORTED_TYPES
from core.context import AppContext
from core.imaging import prepare_image
from services import crack_service
from ui import components as c


def render(ctx: AppContext) -> None:
    st.subheader("Crack diagnostics and structural integrity")
    st.caption("Upload a close-up of a concrete or masonry surface. Include a coin, ruler or brick joint "
               "in the frame so the model can judge the crack width.")

    upload = st.file_uploader("Concrete or wall surface photo", type=SUPPORTED_TYPES, key="crack_upload")
    if upload is None:
        st.info("Upload a JPG or PNG of the defect to begin.")
        return
    try:
        image, digest = prepare_image(upload)
    except ValueError as exc:
        st.error(str(exc))
        return

    left, right = st.columns([2, 3])
    with left:
        st.image(image, caption=upload.name)
        run = st.button("Diagnose defect", type="primary", key="crack_run")

    if run:
        with st.spinner("Classifying the defect..."):
            st.session_state["crack_result"] = {"digest": digest, "result": crack_service.analyze(ctx.client, image, digest)}

    stored = st.session_state.get("crack_result")
    with right:
        if not stored or stored["digest"] != digest:
            st.info("Select **Diagnose defect** to analyse this photo.")
            return
        _render_report(stored["result"])


def _render_report(result) -> None:
    r = result.report
    c.mode_banner(result.mode, result.warning or "", r["meta"]["model"])

    level, score = r["severity_level"], r["severity_score"]
    tone = c.SEVERITY_TONE[level]
    cols = st.columns(4)
    with cols[0]:
        c.metric_card("Defect type", r["defect_type"], r["crack_pattern"][:48], tone)
    with cols[1]:
        c.metric_card("Crack width", f'{r["crack_width_mm"]:.2f} mm', "IS 456 general limit: 0.3 mm", tone)
    with cols[2]:
        c.metric_card("Severity", f"{level} · {score}/100", "Higher means more serious", tone)
    with cols[3]:
        c.metric_card("Model confidence", f'{int(r["confidence"] * 100)}%', "Lower if no scale in frame")
    st.progress(score / 100)

    st.markdown(f'**Urgency:** {c.pill(r["urgency"], tone)}', unsafe_allow_html=True)
    if r["summary"]:
        st.markdown(f"**Summary.** {r['summary']}")

    a, b = st.columns(2)
    with a:
        st.markdown("##### Likely root causes")
        for cause in r["root_causes"] or ["No cause identified."]:
            st.markdown(f"- {cause}")
    with b:
        st.markdown("##### Recommended repairs")
        for step in r["recommended_repairs"] or [{"method": "No repair suggested.", "details": ""}]:
            detail = f": {step['details']}" if step["details"] else ""
            st.markdown(f"- **{step['method']}**{detail}")

    if r["monitoring_plan"]:
        st.markdown(f"**Monitoring plan.** {r['monitoring_plan']}")
    if level in ("High", "Critical"):
        st.error("This finding needs inspection by a licensed structural engineer before repairs begin.")
    c.download_json("Download JSON report", r, "crack_diagnostic_report.json", "crack_dl")
    c.disclaimer()
