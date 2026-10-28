"""Multimodal Construction Intelligence Platform: Streamlit entry point.

Run locally:  streamlit run app.py
"""
import logging

import streamlit as st

from core.config import APP_NAME, APP_TAGLINE

st.set_page_config(page_title=APP_NAME, page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

from core.styles import inject_css  # noqa: E402  (must follow set_page_config)
from ui import tab_assistant, tab_cracks, tab_planning, tab_safety  # noqa: E402
from ui.sidebar import render_sidebar  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

TABS = [
    ("🦺 Safety and PPE", tab_safety.render),
    ("🧱 Crack diagnostics", tab_cracks.render),
    ("📐 Planning and valuation", tab_planning.render),
    ("🌦️ Daily site assistant", tab_assistant.render),
]


def main() -> None:
    inject_css()
    ctx = render_sidebar()
    st.markdown(f'<div class="hero"><div class="hero-title">{APP_NAME}</div>'
                f'<div class="hero-sub">{APP_TAGLINE}</div></div>', unsafe_allow_html=True)

    for tab, (_label, render) in zip(st.tabs([t[0] for t in TABS]), TABS):
        with tab:
            try:
                render(ctx)
            except Exception as exc:  # keep one failing tab from taking down the page
                log.exception("Tab failed")
                st.error(f"Something went wrong in this section: {exc}. Reload the page or clear session data in the sidebar.")


main()
