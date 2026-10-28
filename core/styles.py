"""Visual identity: blueprint ink, concrete grey, hi-vis amber."""
import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600;700&display=swap');

:root {
  --ink: #0f2a43; --ink-2: #1c4166; --concrete: #eef0f2; --line: #d6dbe0; --text: #1f2933; --muted: #5f6b76;
  --amber: #f5a300; --ok: #1e7a46; --warn: #b7791f; --high: #c2410c; --crit: #b42318;
}
/* Apply the font to text elements only. A wildcard here would also hit Streamlit's icon spans
   and print icon names (upload, visibility, ...) as plain text. */
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp button, .stApp input, .stApp textarea, .stApp [data-baseweb="tab"], .stApp [data-testid="stMarkdownContainer"] {
  font-family: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
[data-testid="stIconMaterial"], [class*="material-symbols"], .material-icons {
  font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}
.block-container { padding-top: 1.6rem; max-width: 1240px; }

/* Hero: blueprint grid */
.hero {
  background-color: var(--ink);
  background-image:
    linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px);
  background-size: 28px 28px;
  border-radius: 10px; padding: 1.5rem 1.8rem; margin-bottom: 1.1rem;
  border-bottom: 5px solid var(--amber);
}
.hero-title { font-family: 'IBM Plex Sans Condensed', 'IBM Plex Sans', sans-serif; font-weight: 700;
  font-size: 2.1rem; line-height: 1.15; color: #ffffff; letter-spacing: .2px; }
.hero-sub { color: #c9d6e2; font-size: .98rem; margin-top: .35rem; max-width: 62ch; }

/* Metric cards: the left rule carries the status colour */
.metric-card { background: #fff; border: 1px solid var(--line); border-left: 6px solid var(--ink);
  border-radius: 6px; padding: .8rem 1rem; height: 100%; }
.metric-label { color: var(--muted); font-size: .85rem; }
.metric-value { font-family: 'IBM Plex Sans Condensed', 'IBM Plex Sans', sans-serif; font-weight: 700;
  font-size: 1.8rem; color: var(--ink); line-height: 1.2; }
.metric-sub { color: var(--muted); font-size: .8rem; }
.tone-ok { border-left-color: var(--ok); } .tone-warn { border-left-color: var(--warn); }
.tone-high { border-left-color: var(--high); } .tone-crit { border-left-color: var(--crit); }
.tone-info { border-left-color: var(--amber); }

/* Status pills */
.pill { display: inline-block; padding: .12rem .65rem; border-radius: 4px; font-size: .8rem; font-weight: 600; }
.pill-ok { background: #dff3e6; color: #14532d; } .pill-warn { background: #fdf0d2; color: #7a4b0a; }
.pill-high { background: #fde4d3; color: #9a3412; } .pill-crit { background: #fbdcd8; color: #8c1d14; }
.pill-muted { background: var(--concrete); color: var(--muted); }

/* Findings */
.finding { background: #fff; border: 1px solid var(--line); border-left: 6px solid var(--line);
  border-radius: 6px; padding: .75rem 1rem; margin-bottom: .6rem; }
.finding.sev-low { border-left-color: var(--ok); } .finding.sev-medium { border-left-color: var(--warn); }
.finding.sev-high { border-left-color: var(--high); } .finding.sev-critical { border-left-color: var(--crit); }
.finding-title { font-weight: 600; color: var(--ink); margin-bottom: .15rem; }
.finding-meta { color: var(--muted); font-size: .85rem; }
.finding-body { margin-top: .3rem; font-size: .95rem; }

.ppe-card { background: var(--concrete); border-radius: 6px; padding: .7rem .9rem; height: 100%; }
.ppe-name { font-weight: 600; color: var(--ink); margin-bottom: .3rem; }
.ppe-note { color: var(--muted); font-size: .82rem; margin-top: .35rem; }

/* Milestones */
.milestone { display: flex; align-items: center; gap: .6rem; padding: .3rem 0; color: var(--muted); }
.milestone .dot { width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--line); background: #fff; flex: none; }
.milestone.done { color: var(--text); } .milestone.done .dot { background: var(--ok); border-color: var(--ok); }
.milestone.active { color: var(--ink); font-weight: 600; }
.milestone.active .dot { background: var(--amber); border-color: var(--amber); box-shadow: 0 0 0 4px rgba(245,163,0,.25); }
.milestone small { margin-left: auto; color: var(--muted); font-weight: 400; }

.banner { border-radius: 6px; padding: .55rem .9rem; font-size: .9rem; margin: .4rem 0 .9rem 0; }
.banner-demo { background: #fdf0d2; color: #7a4b0a; border: 1px solid #f1d58f; }
.banner-live { background: #dff3e6; color: #14532d; border: 1px solid #b7e0c4; }
.note { color: var(--muted); font-size: .82rem; }

section[data-testid="stSidebar"] { background: var(--concrete); }
button[kind="primary"] { background: var(--ink); border-color: var(--ink); }
button[kind="primary"]:hover { background: var(--ink-2); border-color: var(--ink-2); }
.stTabs [data-baseweb="tab"] { font-weight: 600; }
.stTabs [aria-selected="true"] { color: var(--ink); }
"""


def inject_css() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
