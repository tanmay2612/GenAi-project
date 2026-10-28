"""Tab 1: Site safety and PPE audit."""
from __future__ import annotations

import streamlit as st

from core.config import SUPPORTED_TYPES
from core.context import AppContext
from core.imaging import prepare_image
from services import safety_service
from ui import components as c


def render(ctx: AppContext) -> None:
    st.subheader("Site safety and PPE audit")
    st.caption("Upload a site photo. The model checks helmets, high-visibility vests, safety boots and "
               "harnesses, and lists hazards with fixes.")

    upload = st.file_uploader("Construction site photo", type=SUPPORTED_TYPES, key="safety_upload")
    if upload is None:
        st.info("Upload a JPG or PNG to begin. The photo should show workers and the work area.")
        return
    try:
        image, digest = prepare_image(upload)
    except ValueError as exc:
        st.error(str(exc))
        return

    left, right = st.columns([2, 3])
    with left:
        st.image(image, caption=upload.name)
        run = st.button("Run PPE audit", type="primary", key="safety_run")

    if run:
        with st.spinner("Auditing the photo..."):
            st.session_state["safety_result"] = {"digest": digest, "result": safety_service.analyze(ctx.client, image, digest)}

    stored = st.session_state.get("safety_result")
    with right:
        if not stored or stored["digest"] != digest:
            st.info("Select **Run PPE audit** to analyse this photo.")
            return
        _render_report(stored["result"], ctx)


def _render_report(result, ctx: AppContext) -> None:
    report = result.report
    c.mode_banner(result.mode, result.warning or "", report["meta"]["model"])

    score, status = report["safety_score"], report["overall_status"]
    critical = sum(1 for h in report["hazards"] if h["severity"] == "Critical")
    cols = st.columns(4)
    with cols[0]:
        c.metric_card("Safety score", f"{score}/100", "100 means fully compliant", c.score_tone(score))
    with cols[1]:
        c.metric_card("Overall status", status, "", c.STATUS_TONE[status])
    with cols[2]:
        c.metric_card("Workers seen", report["workers_detected"], "In this photo")
    with cols[3]:
        c.metric_card("Hazards", len(report["hazards"]), f"{critical} critical", "crit" if critical else "ok")
    st.progress(score / 100)

    if report["summary"]:
        st.markdown(f"**Summary.** {report['summary']}")

    st.markdown("##### PPE checklist")
    ppe = report["ppe_detection"]
    cols = st.columns(min(len(ppe), 4))
    for i, item in enumerate(ppe):
        with cols[i % len(cols)]:
            note = f'<div class="ppe-note">{c.esc(item["notes"])}</div>' if item["notes"] else ""
            c.html_block(f'<div class="ppe-card"><div class="ppe-name">{c.esc(item["item"])}</div>'
                         f'{c.pill(item["status"], c.PPE_TONE[item["status"]])}{note}</div>')

    st.markdown("##### Hazards and corrective actions")
    if not report["hazards"]:
        st.success("No hazards were identified in this photo.")
    for h in report["hazards"]:
        sev = h["severity"]
        c.html_block(
            f'<div class="finding sev-{sev.lower()}"><div class="finding-title">{c.esc(h["hazard"])} '
            f'{c.pill(sev, c.SEVERITY_TONE[sev])}</div><div class="finding-meta">{c.esc(h["location"])}</div>'
            f'<div class="finding-body"><b>Fix:</b> {c.esc(h["remedy"])}</div></div>'
        )

    refs = ", ".join(report["standards_referenced"])
    c.html_block(f'<div class="note">Standards referenced: {c.esc(refs)}</div>')
    c.download_json("Download JSON report", report, "ppe_safety_report.json", "safety_dl")
    c.disclaimer()
