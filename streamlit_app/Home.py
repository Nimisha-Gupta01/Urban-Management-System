"""
Urban Traffic Management System — Home / Landing Page
BITS Pilani WILP | SESAP ZC337
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from api_client import get, apply_light_theme, icon

st.set_page_config(
    page_title="Urban Traffic Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_light_theme()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-size:1.15rem;font-weight:700;color:#1a1a2e;display:flex;'
        f'align-items:center;gap:6px;margin-bottom:0.2rem;">'
        f'{icon("traffic", size="lg", color="#5b7fe8")} UTMS</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Bengaluru · BITS Pilani WILP**")
    st.divider()
    role = st.selectbox(
        "Your Role",
        ["public", "officer", "admin"],
        index=0,
        help="officer/admin can write data; public can only read"
    )
    st.session_state["role"] = role

    role_color = {"public": "#2196f3", "officer": "#ff9800", "admin": "#e53935"}
    st.markdown(
        f'<span style="background:{role_color[role]};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:0.8rem;font-weight:600">{role.upper()}</span>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:0.2rem;">'
    f'{icon("traffic", size="lg", color="#5b7fe8")}'
    f'<span style="font-size:1.8rem;font-weight:700;color:#1a1a2e;">Urban Traffic Management System</span>'
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#555;margin-top:-0.5rem;">Bengaluru, India &nbsp;·&nbsp; '
    'BITS Pilani WILP &nbsp;·&nbsp; SESAP ZC337</p>',
    unsafe_allow_html=True,
)
st.divider()

# ── Live KPIs from API ────────────────────────────────────────────────────────
data, err = get("/api/dashboard")

col1, col2, col3, col4 = st.columns(4)

if data and not err:
    kpis = data.get("city_kpis", {})
    inc  = data.get("incident_summary", {})
    open_count = sum(s["count"] for s in inc) if isinstance(inc, list) else inc.get("open", 0)
    col1.metric("Total Junctions",   len(data.get("junctions", [])))
    col2.metric("Avg Vehicle Count", f"{kpis.get('avg_vehicle_count', 0):.0f}")
    col3.metric("Avg Speed (km/h)",  f"{kpis.get('avg_speed_kmph', 0):.1f}")
    col4.metric("Open Incidents",    open_count)
else:
    col1.metric("Total Junctions", "—")
    col2.metric("Avg Vehicle Count", "—")
    col3.metric("Avg Speed (km/h)", "—")
    col4.metric("Open Incidents", "—")
    if err:
        st.warning(f"API not reachable — {err}")

st.divider()

# ── What's inside ─────────────────────────────────────────────────────────────
st.subheader("What's inside")

left, right = st.columns(2)

CARDS_LEFT = [
    (f'{icon("dashboard", color="#5b7fe8")} Dashboard',
     "Live map of all junctions coloured by congestion level, city KPIs, zone breakdown, and open incident count.",
     "/Dashboard"),
    (f'{icon("sensors", color="#5b7fe8")} Traffic Data',
     "Filter and browse all traffic observations by zone, junction, congestion level, or time window.",
     "/Traffic"),
    (f'{icon("add_road", color="#5b7fe8")} Add Observation',
     "Submit a new traffic observation (officer / admin only). Auto-suggests congestion level from vehicle count.",
     "/Add_Observation"),
]

CARDS_RIGHT = [
    (f'{icon("warning_amber", color="#e53935")} Incidents',
     "View open incidents, report new ones, mark as resolved, or delete (admin only). Full audit trail in DB.",
     "/Incidents"),
    (f'{icon("map", color="#5b7fe8")} Roads & Zones',
     "Browse all roads, junctions, and zones across Bengaluru. Analytics tab shows top congested junctions.",
     "/Roads_Zones"),
]

def render_cards(cards):
    html = ""
    for title, desc, url in cards:
        if url:
            html += (
                f'<a href="{url}" target="_self" style="text-decoration:none;">'
                f'<div class="feature-card clickable-card">'
                f'<h4>{title} <span style="font-size:0.8rem;color:#888;">→</span></h4>'
                f'<p>{desc}</p>'
                f'</div></a>'
            )
        else:
            html += (
                f'<div class="feature-card">'
                f'<h4>{title}</h4>'
                f'<p>{desc}</p>'
                f'</div>'
            )
    st.markdown(html, unsafe_allow_html=True)

with left:
    render_cards(CARDS_LEFT)
with right:
    render_cards(CARDS_RIGHT)

st.divider()
st.caption("BITS Pilani WILP · SESAP ZC337 · Team: Nimisha Gupta (I578445) · Fasi Ahmed Khan (I578459)")
