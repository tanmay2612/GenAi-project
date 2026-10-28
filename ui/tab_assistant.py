"""Tab 4: Daily site assistant and weather-aware advisory."""
from __future__ import annotations

import streamlit as st

from core.context import AppContext
from services import chat_service, weather_service
from ui import components as c

SUGGESTIONS = [
    "How long should I cure a slab?",
    "When can I strip beam formwork?",
    "What cover do I need in a coastal area?",
    "How should I store cement bags?",
]


def render(ctx: AppContext) -> None:
    st.subheader("Daily site assistant")
    weather = st.radio("Today's weather condition", weather_service.CONDITIONS, horizontal=True, key="weather")
    _render_advisory(weather)

    st.divider()
    st.markdown("##### Ask the site engineering assistant")
    history = st.session_state.setdefault("chat_history", [])

    if not history:
        cols = st.columns(len(SUGGESTIONS))
        for col, question in zip(cols, SUGGESTIONS):
            if col.button(question, key=f"sugg_{question}"):
                st.session_state["pending_prompt"] = question
                st.rerun()

    for turn in history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    message = st.chat_input("Ask about curing, safety, quantities, cracks...") or st.session_state.pop("pending_prompt", None)
    if message:
        with st.chat_message("user"):
            st.markdown(message)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply, mode = chat_service.respond(ctx.client, history, message, weather)
            st.markdown(reply)
            if mode == "demo" and not ctx.live:
                st.caption("Demonstration mode: answers come from a built-in knowledge base.")
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
    c.disclaimer()


def _render_advisory(condition: str) -> None:
    adv = weather_service.get_advisory(condition)
    tone = {"Low": "ok", "High": "high"}.get(str(adv["level"]), "warn")
    c.html_block(f'<div class="metric-card tone-{tone}"><div class="metric-label">{adv["icon"]} {c.esc(condition)}</div>'
                 f'<div class="metric-value" style="font-size:1.35rem">{c.esc(adv["headline"])}</div></div>')
    st.write("")
    for title, severity, detail in adv["alerts"]:  # type: ignore[misc]
        c.html_block(f'<div class="finding sev-{severity.lower()}"><div class="finding-title">{c.esc(title)} '
                     f'{c.pill(severity, c.SEVERITY_TONE[severity])}</div><div class="finding-body">{c.esc(detail)}</div></div>')

    a, b, d = st.columns(3)
    a.markdown("**Concrete and curing**")
    a.write(adv["concrete"])
    b.markdown("**Electrical safety**")
    b.write(adv["electrical"])
    d.markdown("**Equipment**")
    d.write(adv["equipment"])
    with st.expander("Daily checklist"):
        for item in adv["checklist"]:  # type: ignore[union-attr]
            st.checkbox(item, key=f"chk_{condition}_{item}")
