"""Sidebar: API key, mode indicator, feature navigation and architecture overview."""
from __future__ import annotations

import streamlit as st

from core.config import APP_NAME, DEFAULT_MODEL
from core.context import AppContext
from core.gemini_client import GeminiClient

ARCHITECTURE = """\
 Streamlit UI (4 tabs)
        |
  services/*  <-- prompts, demo data, calculators
        |
  core/gemini_client.py --> Gemini (multimodal)
        |                    (falls back to demo mode)
  core/schemas.py  --> JSON data contracts
"""

FEATURES = [
    ("🦺", "Safety and PPE audit", "Photo to safety score, PPE checklist and hazards"),
    ("🧱", "Crack diagnostics", "Defect type, width, severity and repair plan"),
    ("📐", "Planning and valuation", "Budget, spend, asset value and materials in INR"),
    ("🌦️", "Site assistant", "Weather protocols and a chat assistant"),
]


def _secret_key() -> str:
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:  # no secrets file configured
        return ""


def render_sidebar() -> AppContext:
    with st.sidebar:
        st.markdown(f"### 🏗️ {APP_NAME}")

        st.markdown("**Gemini API access**")
        typed = st.text_input(
            "Google Gemini API key", type="password", placeholder="Paste your key",
            help="Kept in this browser session only. It is never written to disk or logged.",
        ).strip()
        model = st.text_input("Model", value=DEFAULT_MODEL,
                              help="Any Gemini model that accepts images. Change it if your account uses a different one.")
        key = typed or _secret_key()

        cached = st.session_state.get("_client")
        if cached is None or cached.api_key != key or cached.model != model.strip():
            cached = GeminiClient(key, model)
            st.session_state["_client"] = cached
        client: GeminiClient = cached

        if client.enabled:
            st.success("Live mode: analyses use your Gemini key.")
        else:
            st.warning("Demonstration mode: sample outputs are shown until you add a key.")
        st.caption("Get a free key at aistudio.google.com/apikey")

        st.divider()
        st.markdown("**What this app does**")
        for icon, title, blurb in FEATURES:
            st.markdown(f"{icon} **{title}**  \n<span class='note'>{blurb}</span>", unsafe_allow_html=True)

        with st.expander("Architecture overview"):
            st.code(ARCHITECTURE, language="text")
            st.caption("No database. All state lives in the browser session, so the app deploys to "
                       "Streamlit Community Cloud with no extra services.")

        if st.button("Clear session data"):
            for k in [k for k in st.session_state.keys() if k != "_client"]:
                del st.session_state[k]
            st.rerun()

    return AppContext(client=client)
