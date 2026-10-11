"""
Urban Traffic Management System — Streamlit Frontend
BITS Pilani WILP | SESAP ZC337
streamlit_app/app.py — Main entry point (multi-page via st.navigation)

Screens:
  1. Dashboard       — KPIs + map + junction table
  2. Traffic Data    — search/filter observations
  3. Add Observation — POST new traffic observation
  4. Incidents       — view/report/resolve incidents
  5. Roads & Zones   — browse roads, junctions, zones, analytics
"""

import streamlit as st

st.set_page_config(
    page_title="Urban Traffic Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Role selector (sidebar) ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚦 Urban Traffic Mgmt")
    st.markdown("**Bengaluru — BITS Pilani WILP**")
    st.divider()
    role = st.selectbox(
        "Simulated Role",
        ["public", "officer", "admin"],
        index=0,
        help="Simulates RBAC: officer/admin can write; public can only read"
    )
    st.session_state["role"] = role
    st.caption(f"Active role: **{role}**")

# ── Navigation ────────────────────────────────────────────────────────────────
pages = {
    "📊 Dashboard":        "pages/1_Dashboard.py",
    "🚗 Traffic Data":     "pages/2_Traffic.py",
    "➕ Add Observation":  "pages/3_Add_Observation.py",
    "🚨 Incidents":        "pages/4_Incidents.py",
    "🛣️ Roads & Zones":   "pages/5_Roads_Zones.py",
}

st.sidebar.divider()
st.sidebar.markdown("### Navigation")
for label in pages:
    st.sidebar.markdown(f"[{label}]({label.split(' ', 1)[1].lower().replace(' & ', '-').replace(' ', '-')})")

# Default landing: show dashboard summary
st.title("🚦 Urban Traffic Management System")
st.markdown("**Bengaluru, India · BITS Pilani WILP · SESAP ZC337**")
st.info("Use the sidebar to navigate between screens. Select your role to simulate RBAC.")
