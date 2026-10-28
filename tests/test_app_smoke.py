from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_starts_without_errors():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert len(at.tabs) == 4


def test_planning_slider_updates_milestone():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.slider(key="plan_completion").set_value(100).run()
    assert not at.exception
    assert any("Handover" in str(m.value) for m in at.markdown)


def test_chat_suggestion_gets_demo_answer():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.button(key="sugg_How long should I cure a slab?").click().run()
    assert not at.exception
    assert any("IS 456" in str(m.value) for m in at.chat_message[1].markdown)
