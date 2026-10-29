"""Screen 3: Add Observation — POST new traffic observation (officer/admin only)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
from api_client import get, post, apply_light_theme, show_table, icon

st.set_page_config(page_title="Add Observation — Urban Traffic", page_icon="➕", layout="wide")
role = st.session_state.get("role", "public")
apply_light_theme()

st.markdown(
    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:0.2rem;">'
    f'{icon("add_road", size="lg", color="#5b7fe8")}'
    f'<span style="font-size:1.8rem;font-weight:700;color:#1a1a2e;">Add Traffic Observation</span>'
    f'</div>',
    unsafe_allow_html=True,
)
st.caption("POST a new observation — demonstrates ACID transaction T1 + PostgreSQL trigger")

if role == "public":
    st.warning("⚠️ You are in **Public** role. Switch to **Officer** or **Admin** in the sidebar to submit.")

# ── Cascade dropdowns: Zone → Junction ───────────────────────────────────────
zones_data, _ = get("/api/zones", role=role)
zone_options = {z["zone_name"]: z["zone_id"] for z in (zones_data or [])}

col1, col2 = st.columns(2)
with col1:
    sel_zone = st.selectbox("Zone *", list(zone_options.keys()))

junctions_data, _ = get("/api/junctions", params={"zone_id": zone_options.get(sel_zone)}, role=role)
junc_options = {j["junction_name"]: j["junction_id"] for j in (junctions_data or [])}

roads_data, _ = get("/api/roads", params={"zone_id": zone_options.get(sel_zone)}, role=role)
road_options = {r["road_name"]: r["road_id"] for r in (roads_data or [])}

with col2:
    sel_junc = st.selectbox("Junction *", list(junc_options.keys()) if junc_options else ["—"])

col3, col4 = st.columns(2)
with col3:
    sel_road = st.selectbox("Road *", list(road_options.keys()) if road_options else ["—"])
with col4:
    data_source = st.selectbox("Data Source *", ["Sensor", "Camera", "Manual", "API"])

col5, col6, col7 = st.columns(3)
with col5:
    vehicle_count = st.number_input("Vehicle Count *", min_value=0, max_value=2000, value=100)
with col6:
    avg_speed = st.number_input("Avg Speed (km/h) *", min_value=0.0, max_value=200.0, value=40.0, step=0.5)
with col7:
    weather = st.selectbox("Weather", ["Clear", "Rainy", "Foggy", "Cloudy", "Stormy"])

# Auto-suggest congestion level
if vehicle_count >= 250:
    suggested = "SEVERE"
elif vehicle_count >= 200:
    suggested = "HIGH"
elif vehicle_count >= 100:
    suggested = "MODERATE"
else:
    suggested = "LOW"

congestion = st.selectbox(
    "Congestion Level *",
    ["LOW", "MODERATE", "HIGH", "SEVERE"],
    index=["LOW", "MODERATE", "HIGH", "SEVERE"].index(suggested),
    help=f"Auto-suggested: {suggested} based on vehicle count"
)

st.caption(f"💡 Auto-suggested: **{suggested}** based on {vehicle_count} vehicles")

# ── Submit ────────────────────────────────────────────────────────────────────
st.divider()
if st.button("Submit Observation", type="primary", disabled=(role == "public")):
    if sel_junc == "—" or sel_road == "—":
        st.error("Please select a valid junction and road.")
    else:
        payload = {
            "junction_id":    junc_options[sel_junc],
            "road_id":        road_options[sel_road],
            "vehicle_count":  int(vehicle_count),
            "avg_speed_kmph": float(avg_speed),
            "congestion_level": congestion,
            "weather_condition": weather,
            "data_source": data_source,
        }
        result, err = post("/api/traffic", payload, role=role)
        if err:
            st.error(f"Failed: {err}")
        else:
            st.success(f"✅ Observation recorded! ID: {result.get('obs_id')} — Trigger will update junction congestion status.")

# ── Recent observations for selected junction ─────────────────────────────────
st.divider()
st.subheader(f"Recent observations at {sel_junc}")
if sel_junc != "—" and sel_junc in junc_options:
    recent, _ = get("/api/traffic", params={"junction_id": junc_options[sel_junc], "limit": 10, "hours": 720}, role=role)
    if recent:
        df = pd.DataFrame(recent)
        cols = [c for c in ["observation_time","road_name","vehicle_count","avg_speed_kmph","congestion_level","weather_condition"] if c in df.columns]
        show_table(df[cols].head(10).fillna("—"))
    else:
        st.info("No recent observations for this junction.")
