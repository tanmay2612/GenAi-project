# Multimodal Construction Intelligence Platform

Skill Wallet Capstone, Project 1. A Streamlit app that turns site photos and a few project inputs into
safety audits, crack diagnoses, INR cost and valuation estimates, and weather-aware daily protocols.

It works with **no API key** (demonstration mode) and with **no database**, so it deploys to Streamlit
Community Cloud in one click.

## What it does

| Tab | Epic | Output |
|---|---|---|
| Safety and PPE | 2 | Safety score (0-100), status, PPE checklist (helmet, vest, boots, harness), hazards with severity and remedies, JSON download |
| Crack diagnostics | 2 | Defect type (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling), width in mm, severity score, root causes, repairs, urgency |
| Planning and valuation | 3 | Budget, capex incurred, current asset value and value on completion in Lakhs/Crores, steel and cement needs, milestone tracker, Pollinations 3D concept render |
| Daily site assistant | 5 | Weather protocols (High Wind, Heavy Rain, Extreme Heat, Normal) and a multi-turn engineering chatbot |

## Run locally

Requires Python 3.9 or newer (3.10+ recommended).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Paste your Gemini key in the sidebar (free key: https://aistudio.google.com/apikey), or set it once:

```bash
mkdir -p .streamlit && cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit GEMINI_API_KEY
```

The default model is `gemini-2.5-flash`. If your account uses another Gemini model, change the **Model**
field in the sidebar; no code change is needed.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. On share.streamlit.io choose **New app**, select the repo, and set the main file to `app.py`.
3. Optional: under **Advanced settings > Secrets** add `GEMINI_API_KEY = "..."`.

## Project structure

```
app.py                 entry point: page config, hero, four tabs, per-tab error isolation
core/
  config.py            constants (PPE items, severities, defect types, limits)
  schemas.py           JSON data contracts: parsing + normalisation (Epic 4)
  gemini_client.py     the only file that talks to the model API
  imaging.py           upload validation, EXIF fix, resize
  styles.py            CSS theme
services/              prompts, demo data and calculators (no Streamlit code)
  analysis.py          live model first, demo fallback on any failure
  safety_service.py  crack_service.py  valuation_service.py  weather_service.py  chat_service.py
ui/                    Streamlit rendering for each tab and the sidebar
contracts/             example JSON for each report type
tests/                 29 pytest tests, including Streamlit AppTest smoke tests
```

## JSON data contracts (Epic 4)

The model is asked for strict JSON. Every reply is parsed and then normalised by
`core/schemas.py` before the UI sees it: scores are clamped to 0-100, severities are mapped to
Low/Medium/High/Critical, missing PPE items are filled in as "Not Visible", and the status is never
softer than the score implies. Crack severity is also never softer than the measured width implies
(IS 456 cl. 35.3.2, 0.3 mm). Demo data goes through the same normaliser, so both modes produce the same
shape. See `contracts/*.example.json`.

## Graceful degradation

- No API key: demonstration reports and a built-in knowledge-base chatbot.
- Key set but the call fails (quota, network, bad model name): the app shows a warning and falls back to
  demonstration output rather than crashing.
- A bug in one tab shows an error in that tab only.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Assumptions and limits

- Construction rates, tier multipliers, market values per sq ft and the steel/cement thumb rules in
  `services/valuation_service.py` are illustrative. Replace them with local rate cards.
- Pollinations renders are conceptual images, not drawings.
- Demo-mode photo analysis does not look at the image: it picks one of several sample reports from the
  file's hash. Use a Gemini key for real analysis.
- Output is decision support, not a substitute for a certified safety officer or structural engineer.
