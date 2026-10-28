"""Small reusable UI building blocks."""
from __future__ import annotations

import html
import json
from typing import Any, Dict

import streamlit as st

from core.config import DISCLAIMER

SEVERITY_TONE = {"Low": "ok", "Medium": "warn", "High": "high", "Critical": "crit"}
STATUS_TONE = {"Compliant": "ok", "Needs Improvement": "warn", "Non-Compliant": "high", "Critical": "crit"}
PPE_TONE = {"Detected": "ok", "Missing": "crit", "Not Visible": "muted"}


def esc(value: Any) -> str:
    return html.escape(str(value))


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def pill(text: str, tone: str) -> str:
    return f'<span class="pill pill-{tone}">{esc(text)}</span>'


def metric_card(label: str, value: Any, sub: str = "", tone: str = "") -> None:
    cls = f" tone-{tone}" if tone else ""
    html_block(
        f'<div class="metric-card{cls}"><div class="metric-label">{esc(label)}</div>'
        f'<div class="metric-value">{esc(value)}</div><div class="metric-sub">{esc(sub)}</div></div>'
    )


def score_tone(score: float) -> str:
    return "ok" if score >= 85 else "warn" if score >= 65 else "high" if score >= 40 else "crit"


def mode_banner(mode: str, warning: str = "", model: str = "") -> None:
    if warning:
        st.warning(warning)
    if mode == "demo":
        html_block('<div class="banner banner-demo"><b>Demonstration output.</b> Add a Gemini API key in the '
                   'sidebar to analyse your own image with the live model.</div>')
    else:
        html_block(f'<div class="banner banner-live">Analysed live with <b>{esc(model)}</b>.</div>')


def download_json(label: str, report: Dict[str, Any], filename: str, key: str) -> None:
    st.download_button(label, data=json.dumps(report, indent=2, ensure_ascii=False),
                       file_name=filename, mime="application/json", key=key)


def disclaimer() -> None:
    html_block(f'<div class="note">{esc(DISCLAIMER)}</div>')
