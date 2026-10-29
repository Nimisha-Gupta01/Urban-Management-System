"""Shared API client and UI helpers for Streamlit pages."""
import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

ROLE_HEADERS = {
    "public":  {"X-User-Role": "public"},
    "officer": {"X-User-Role": "officer"},
    "admin":   {"X-User-Role": "admin"},
}

LIGHT_CSS = """
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    /* ── Material Icons baseline alignment ──────────────────────────── */
    .material-icons {
        font-size: 18px;
        vertical-align: middle;
        line-height: 1;
    }
    .mat-icon-lg  { font-size: 26px !important; vertical-align: middle; line-height: 1; }
    .mat-icon-sm  { font-size: 15px !important; vertical-align: middle; line-height: 1; }
    .mat-icon-accent { color: #5b7fe8 !important; }

    /* ── Global background + body text ──────────────────────────────── */
    .stApp, .main, .block-container {
        background-color: #f7f8fa !important;
        color: #1a1a2e !important;
    }
    body, p, span, div, label, li {
        color: #1a1a2e !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e4ea;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a2e !important;
    }

    /* ── Sidebar collapse/expand button ─────────────────────────────── */
    [data-testid="collapsedControl"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e4ea !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #1a1a2e !important;
        color: #1a1a2e !important;
    }
    button[kind="header"] {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }

    /* ── Headings ────────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a2e !important;
    }

    /* ── Caption / small text ────────────────────────────────────────── */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    small, .caption {
        color: #666 !important;
    }

    /* ── KPI metric cards ────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e0e4ea;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] p { color: #666 !important; font-size: 0.82rem !important; }
    [data-testid="stMetricValue"]   { color: #1a1a2e !important; font-size: 1.6rem !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"]   { font-size: 0.8rem !important; }

    /* ── Tabs ────────────────────────────────────────────────────────── */
    [data-testid="stTabs"] [role="tablist"] {
        background: #ffffff;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #e0e4ea;
    }
    [data-testid="stTabs"] button {
        color: #555 !important;
        font-weight: 500;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #1a1a2e !important;
        border-bottom: 2px solid #1a1a2e !important;
    }
    [data-testid="stTabsContent"] {
        background: #ffffff;
        border: 1px solid #e0e4ea;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }

    /* ── Expander ────────────────────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e0e4ea !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: #1a1a2e !important;
        font-weight: 500;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #fafbfc !important;
    }

    /* ── Inputs / selects / sliders ──────────────────────────────────── */
    [data-testid="stSelectbox"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stSlider"] label,
    [data-testid="stCheckbox"] label {
        color: #333 !important;
        font-weight: 500;
    }
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #1a1a2e !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
    }

    /* ── Selectbox dropdown popup (BaseWeb popover) ──────────────────── */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] [role="listbox"] {
        background-color: #ffffff !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] [role="option"] {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }
    [data-baseweb="popover"] li:hover,
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {
        background-color: #e8ecf8 !important;
        color: #1a1a2e !important;
    }
    /* menu list container */
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] [role="option"] {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [role="option"]:hover {
        background-color: #e8ecf8 !important;
        color: #1a1a2e !important;
    }

    /* ── Dataframe / table ───────────────────────────────────────────── */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrameResizable"] {
        background: #ffffff !important;
        border: 1px solid #dde3f0 !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    /* Header row */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrameResizable"] th {
        background: #e8ecf8 !important;
        color: #2c3e7a !important;
        font-weight: 650 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.03em;
        border-bottom: 2px solid #c5cef0 !important;
    }
    /* Body rows */
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrameResizable"] td {
        color: #2d3748 !important;
        font-size: 0.85rem !important;
    }
    /* Alternating row tint */
    [data-testid="stDataFrame"] tr:nth-child(even) td {
        background: #f4f6fc !important;
    }
    [data-testid="stDataFrame"] tr:hover td {
        background: #eaedfa !important;
    }

    /* ── Alert boxes (info / warning / error / success) ─────────────── */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
    }
    /* info */
    [data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
        background: #e8f4fd !important; color: #1a5276 !important;
    }
    /* warning */
    [data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
        background: #fef9e7 !important; color: #7d6608 !important;
    }
    /* success */
    [data-testid="stAlert"][data-baseweb="notification"][kind="success"] {
        background: #eafaf1 !important; color: #1e8449 !important;
    }
    /* error */
    [data-testid="stAlert"][data-baseweb="notification"][kind="error"] {
        background: #fdedec !important; color: #922b21 !important;
    }

    /* ── Bar chart labels ────────────────────────────────────────────── */
    .vega-embed text, .vega-embed .mark-text text {
        fill: #1a1a2e !important;
    }

    /* ── Divider ─────────────────────────────────────────────────────── */
    hr { border-color: #e0e4ea !important; }

    /* ── Feature cards (Home page) ───────────────────────────────────── */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e0e4ea;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .feature-card h4 { margin: 0 0 0.3rem 0; color: #1a1a2e !important; font-size: 1rem; }
    .feature-card p  { margin: 0; color: #555 !important; font-size: 0.85rem; }
    a .feature-card, a:visited .feature-card { color: inherit !important; text-decoration: none !important; }
    a .feature-card h4 { color: #1a1a2e !important; }
    a .feature-card p  { color: #555 !important; }
    .clickable-card  { cursor: pointer; transition: box-shadow 0.15s, border-color 0.15s; }
    .clickable-card:hover {
        border-color: #1a1a2e !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
    }

    /* ── Markdown text inside st.markdown ───────────────────────────── */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span {
        color: #1a1a2e !important;
    }

    /* ── Button ──────────────────────────────────────────────────────── */
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-secondary"] p,
    [data-testid="baseButton-secondary"] span {
        background: #ffffff !important;
        color: #1a1a2e !important;
        border: 1px solid #ced4da !important;
    }
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-primary"] p,
    [data-testid="baseButton-primary"] span {
        background: #1a1a2e !important;
        color: #ffffff !important;
        border: none !important;
    }
</style>
"""


def apply_light_theme():
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)


def show_table(df):
    """Render a pandas DataFrame as a light-themed HTML table."""
    html = df.to_html(index=False, border=0, classes="utms-table")
    st.markdown(f"""
<style>
.utms-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    font-family: sans-serif;
    background: #ffffff;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #dde3f0;
}}
.utms-table thead tr {{
    background: #e8ecf8;
}}
.utms-table th {{
    padding: 10px 14px;
    text-align: left;
    color: #2c3e7a;
    font-weight: 650;
    font-size: 0.8rem;
    letter-spacing: 0.03em;
    border-bottom: 2px solid #c5cef0;
    white-space: nowrap;
}}
.utms-table td {{
    padding: 9px 14px;
    color: #2d3748;
    border-bottom: 1px solid #eef0f7;
}}
.utms-table tbody tr:nth-child(even) td {{
    background: #f4f6fc;
}}
.utms-table tbody tr:hover td {{
    background: #eaedfa;
}}
</style>
{html}
""", unsafe_allow_html=True)


def _headers(role="public"):
    return ROLE_HEADERS.get(role, ROLE_HEADERS["public"])


# Static reference data (zones, roads, junctions) — cache for 10 minutes
@st.cache_data(ttl=600, show_spinner=False)
def _get_static(path, params_key, role):
    try:
        params = dict(p.split("=") for p in params_key.split("&") if p) if params_key else None
        r = requests.get(f"{API_BASE}{path}", params=params, headers=_headers(role), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


# Live data (traffic, dashboard, incidents) — cache for 60 seconds
@st.cache_data(ttl=60, show_spinner=False)
def _get_live(path, params_key, role):
    try:
        params = dict(p.split("=") for p in params_key.split("&") if p) if params_key else None
        r = requests.get(f"{API_BASE}{path}", params=params, headers=_headers(role), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server. Make sure FastAPI is running on port 8000."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


_STATIC_PATHS = {"/api/zones", "/api/roads", "/api/junctions"}


def get(path, params=None, role="public"):
    # Serialise params dict to a stable string key for cache
    params_key = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
    if path in _STATIC_PATHS:
        return _get_static(path, params_key, role)
    return _get_live(path, params_key, role)


def _bust_cache():
    """Clear live cache after any write so data reflects the change instantly."""
    _get_live.clear()


def post(path, data, role="public"):
    try:
        r = requests.post(f"{API_BASE}{path}", json=data, headers=_headers(role), timeout=10)
        r.raise_for_status()
        _bust_cache()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def put(path, data, role="public"):
    try:
        r = requests.put(f"{API_BASE}{path}", json=data, headers=_headers(role), timeout=10)
        r.raise_for_status()
        _bust_cache()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def delete(path, role="public"):
    try:
        r = requests.delete(f"{API_BASE}{path}", headers=_headers(role), timeout=10)
        r.raise_for_status()
        _bust_cache()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def icon(name: str, *, size: str = "", color: str = "", extra: str = "") -> str:
    classes = "material-icons"
    if size:
        classes += f" mat-icon-{size}"
    style_parts = []
    if color:
        style_parts.append(f"color:{color}")
    if extra:
        style_parts.append(extra)
    style_attr = f' style="{";".join(style_parts)}"' if style_parts else ""
    return f'<span class="{classes}"{style_attr}>{name}</span>'
