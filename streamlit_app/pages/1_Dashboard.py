"""Screen 1: Dashboard — KPIs, map, junction status, incident summary."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
from api_client import get, apply_light_theme, show_table

st.set_page_config(page_title="Dashboard — Urban Traffic", page_icon="📊", layout="wide")
import time

role = st.session_state.get("role", "public")
apply_light_theme()

with st.sidebar:
    live_mode = st.toggle("🔴 Live Mode", value=False,
                          help="Auto-refresh every 30 seconds")
    if live_mode:
        st.caption("Refreshing every 30s...")

st.title("📊 Traffic Dashboard")
st.caption("Live traffic conditions across Bengaluru junctions · auto-data from FastAPI + PostgreSQL")

# ── Fetch data ────────────────────────────────────────────────────────────────
dashboard, err = get("/api/dashboard", role=role)
map_data, map_err = get("/api/map", role=role)

if err:
    st.error(f"Could not load dashboard: {err}")
    st.stop()

kpis     = dashboard.get("city_kpis", {})
junctions = dashboard.get("junctions", [])
zones    = dashboard.get("zones", [])
inc_summ = dashboard.get("incident_summary", [])

# ── KPI cards ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Observations (24h)", kpis.get("total_observations_24h", 0))
col2.metric("Avg Vehicles / Junction", kpis.get("city_avg_vehicles", "—"))
col3.metric("Avg Speed (km/h)", kpis.get("city_avg_speed", "—"))
col4.metric("High Congestion Junctions", kpis.get("high_congestion_count", 0))

st.divider()

# ── Map ───────────────────────────────────────────────────────────────────────
st.subheader("🗺️ Junction Map — Real Bengaluru Locations")

COLOUR = {
    "SEVERE":   "red",
    "HIGH":     "orange",
    "MODERATE": "blue",
    "LOW":      "green",
    None:       "gray",
}

if map_data:
    m = folium.Map(location=[12.972, 77.64], zoom_start=12, tiles="OpenStreetMap")

    for j in map_data.get("junctions", []):
        level = j.get("congestion_level")
        color = COLOUR.get(level, "gray")
        size  = max(6, min(20, (j.get("vehicle_count") or 0) // 15))
        popup_html = f"""
        <b>{j['junction_name']}</b><br>
        Zone: {j['zone_name']}<br>
        Congestion: <b>{level or 'No data'}</b><br>
        Vehicles: {j.get('vehicle_count', '—')}<br>
        Avg Speed: {j.get('avg_speed_kmph', '—')} km/h
        """
        folium.CircleMarker(
            location=[j["latitude"], j["longitude"]],
            radius=size,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=j["junction_name"],
        ).add_to(m)

    for i in map_data.get("incidents", []):
        if i.get("latitude"):
            folium.Marker(
                location=[i["latitude"], i["longitude"]],
                icon=folium.Icon(color="red", icon="exclamation-sign"),
                popup=f"{i['incident_type']} — {i['severity']}<br>{i.get('description', '')}",
                tooltip=f"⚠️ {i['incident_type']}",
            ).add_to(m)

    st_folium(m, width="100%", height=400, returned_objects=[])
else:
    st.warning("Map data unavailable.")

st.divider()

# ── Junction status table ─────────────────────────────────────────────────────
st.subheader("🚦 Junction Status")
if junctions:
    df = pd.DataFrame(junctions)
    cols = [c for c in ["junction_name", "zone_name", "congestion_level", "vehicle_count",
                        "avg_speed_kmph", "weather_condition", "signal_status"] if c in df.columns]
    show_table(df[cols].fillna("—"))
else:
    st.info("No junction data.")

# ── Zone summary ──────────────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("🏙️ Zone Summary")
    if zones:
        df_z = pd.DataFrame(zones)
        cols = [c for c in ["zone_name", "zone_type", "total_junctions", "total_roads",
                            "observations_last_24h", "avg_vehicle_count", "open_incidents"] if c in df_z.columns]
        show_table(df_z[cols].fillna(0))

with right:
    st.subheader("🚨 Open Incidents by Severity")
    if inc_summ:
        df_i = pd.DataFrame(inc_summ)
        sev_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        sev_colors = {"CRITICAL": "#e53935", "HIGH": "#ff7043", "MEDIUM": "#ffa726", "LOW": "#66bb6a"}
        df_i["color"] = df_i["severity"].map(sev_colors).fillna("#5b7fe8")
        chart = alt.Chart(df_i).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("severity:O", sort=sev_order, title=None, axis=alt.Axis(labelColor="#555")),
            y=alt.Y("count:Q", title="Incidents", axis=alt.Axis(labelColor="#555", titleColor="#333")),
            color=alt.Color("severity:N", scale=alt.Scale(
                domain=list(sev_colors.keys()), range=list(sev_colors.values())
            ), legend=None),
            tooltip=["severity", "count"],
        ).properties(height=220, background="#ffffff").configure_view(strokeOpacity=0).configure_axis(gridColor="#e8ecf8")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.success("No open incidents.")

# ── Auto-refresh when live mode is on ────────────────────────────────────────
if live_mode:
    placeholder = st.empty()
    for remaining in range(30, 0, -1):
        placeholder.caption(f"Next refresh in {remaining}s...")
        time.sleep(1)
    placeholder.empty()
    st.rerun()
