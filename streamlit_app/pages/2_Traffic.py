"""Screen 2: Traffic Data — search and filter observations."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
from api_client import get

st.set_page_config(page_title="Traffic Data — Urban Traffic", page_icon="🚗", layout="wide")
role = st.session_state.get("role", "public")

st.title("🚗 Traffic Observations")
st.caption("Search and filter traffic observations from PostgreSQL")

# ── Filters ───────────────────────────────────────────────────────────────────
zones_data, _ = get("/api/zones", role=role)
junctions_data, _ = get("/api/junctions", role=role)

zone_options = {z["zone_name"]: z["zone_id"] for z in (zones_data or [])}
junc_options = {j["junction_name"]: j["junction_id"] for j in (junctions_data or [])}

with st.expander("🔍 Filters", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sel_zone = st.selectbox("Zone", ["All"] + list(zone_options.keys()))
    with col2:
        sel_junc = st.selectbox("Junction", ["All"] + list(junc_options.keys()))
    with col3:
        sel_cong = st.selectbox("Congestion Level", ["All", "LOW", "MODERATE", "HIGH", "SEVERE"])
    with col4:
        hours = st.slider("Time Window (hours)", 1, 720, 24)

params = {"hours": hours, "limit": 200}
if sel_zone != "All":
    pass  # filter client-side since API doesn't accept zone_id on /traffic
if sel_junc != "All":
    params["junction_id"] = junc_options[sel_junc]
if sel_cong != "All":
    params["congestion_level"] = sel_cong

data, err = get("/api/traffic", params=params, role=role)

if err:
    st.error(err)
    st.stop()

if not data:
    st.info("No observations found for the selected filters.")
    st.stop()

df = pd.DataFrame(data)

# Apply zone filter client-side
if sel_zone != "All":
    df = df[df["zone_name"] == sel_zone]

st.markdown(f"**{len(df)} observations** found")

# ── Summary metrics ───────────────────────────────────────────────────────────
if not df.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Vehicle Count", f"{df['vehicle_count'].mean():.0f}")
    c2.metric("Avg Speed (km/h)", f"{df['avg_speed_kmph'].mean():.1f}")
    c3.metric("Severe/High Congestion", int((df['congestion_level'].isin(['SEVERE','HIGH'])).sum()))

    st.divider()

    # ── Peak hours bar chart ──────────────────────────────────────────────────
    st.subheader("⏰ Peak Hours (avg vehicles)")
    ph_data, _ = get("/api/analytics/peak-hours", role=role)
    if ph_data:
        df_ph = pd.DataFrame(ph_data).sort_values("hour_of_day")
        if not df_ph.empty:
            st.bar_chart(df_ph.set_index("hour_of_day")["avg_vehicles"])

    st.divider()

    # ── Results table ─────────────────────────────────────────────────────────
    st.subheader("📋 Observation Records")
    show_cols = [c for c in ["observation_time", "junction_name", "road_name", "zone_name",
                             "vehicle_count", "avg_speed_kmph", "congestion_level",
                             "weather_condition", "data_source"] if c in df.columns]
    st.dataframe(df[show_cols].fillna("—"), use_container_width=True, hide_index=True)
