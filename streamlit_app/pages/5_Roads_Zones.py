"""Screen 5: Roads & Zones — browse roads, junctions, zones, analytics."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import altair as alt
from api_client import get, apply_light_theme, show_table

st.set_page_config(page_title="Roads & Zones — Urban Traffic", page_icon="🛣️", layout="wide")
role = st.session_state.get("role", "public")
apply_light_theme()

st.title("🛣️ Roads, Junctions & Zones")
st.caption("Browse the road network and zone analytics")

tab_roads, tab_junctions, tab_zones, tab_analytics, tab_signals = st.tabs(
    ["🛣️ Roads", "🚦 Junctions", "🏙️ Zones", "📈 Analytics", "🚥 Signals"]
)

# ── Tab 1: Roads ──────────────────────────────────────────────────────────────
with tab_roads:
    zones_data, _ = get("/api/zones", role=role)
    zone_opts = {"All": None} | {z["zone_name"]: z["zone_id"] for z in (zones_data or [])}

    col1, col2 = st.columns(2)
    with col1:
        sel_zone = st.selectbox("Filter by Zone", list(zone_opts.keys()), key="road_zone")
    with col2:
        road_type = st.selectbox("Road Type", ["All", "National Highway", "State Highway",
                                                "City Road", "Ring Road", "Flyover", "Lane"])

    params = {}
    if zone_opts[sel_zone]:
        params["zone_id"] = zone_opts[sel_zone]
    if road_type != "All":
        params["road_type"] = road_type

    roads, err = get("/api/roads", params=params, role=role)
    if err:
        st.error(err)
    elif roads:
        df = pd.DataFrame(roads)
        cols = [c for c in ["road_name", "road_type", "length_km", "num_lanes",
                            "speed_limit", "surface_type", "direction_type", "zone_name"] if c in df.columns]
        show_table(df[cols].fillna("—"))
        st.caption(f"{len(df)} roads")
    else:
        st.info("No roads found.")

# ── Tab 2: Junctions ──────────────────────────────────────────────────────────
with tab_junctions:
    zones_data2, _ = get("/api/zones", role=role)
    zone_opts2 = {"All": None} | {z["zone_name"]: z["zone_id"] for z in (zones_data2 or [])}
    sel_zone2 = st.selectbox("Filter by Zone", list(zone_opts2.keys()), key="junc_zone")

    params2 = {}
    if zone_opts2[sel_zone2]:
        params2["zone_id"] = zone_opts2[sel_zone2]

    junctions, err2 = get("/api/junctions", params=params2, role=role)
    if err2:
        st.error(err2)
    elif junctions:
        df_j = pd.DataFrame(junctions)
        cols_j = [c for c in ["junction_name", "junction_type", "zone_name", "latitude",
                              "longitude", "signal_controlled", "congestion_status"] if c in df_j.columns]
        show_table(df_j[cols_j].fillna("—"))
        st.caption(f"{len(df_j)} junctions")
    else:
        st.info("No junctions found.")

# ── Tab 3: Zones ──────────────────────────────────────────────────────────────
with tab_zones:
    zones_all, err3 = get("/api/analytics/zone-summary", role=role)
    if err3:
        st.error(err3)
    elif zones_all:
        df_z = pd.DataFrame(zones_all)
        cols_z = [c for c in ["zone_name", "zone_type", "total_junctions", "total_roads",
                              "observations_last_24h", "avg_vehicle_count", "avg_speed_kmph",
                              "open_incidents"] if c in df_z.columns]
        show_table(df_z[cols_z].fillna(0))
    else:
        st.info("No zone data.")

# ── Tab 4: Analytics ─────────────────────────────────────────────────────────
with tab_analytics:
    st.subheader("🏆 Top 5 Most Congested Junctions (Last 24h)")
    top5, err4 = get("/api/analytics/top-congested", role=role)
    if err4:
        st.error(err4)
    elif top5:
        df_t = pd.DataFrame(top5)
        show_table(df_t.fillna("—"))
        if "avg_vehicles" in df_t.columns and "junction_name" in df_t.columns:
            chart = alt.Chart(df_t).mark_bar(color="#5b7fe8", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("avg_vehicles:Q", title="Avg Vehicles", axis=alt.Axis(labelColor="#555", titleColor="#333")),
                y=alt.Y("junction_name:N", sort="-x", title=None, axis=alt.Axis(labelColor="#333")),
                tooltip=["junction_name", "avg_vehicles"],
            ).properties(height=220, background="#ffffff").configure_view(strokeOpacity=0).configure_axis(gridColor="#e8ecf8")
            st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No congestion data in last 24 hours.")

# ── Tab 5: Signals ────────────────────────────────────────────────────────────
with tab_signals:
    st.subheader("🚥 Traffic Signal Status")
    st.caption("Green phase durations are updated automatically by the adaptive signal engine")

    signals_data, sig_err = get("/api/signals", role=role)
    if sig_err:
        st.info("Signal data not available.")
    elif signals_data:
        df_sig = pd.DataFrame(signals_data)
        cols_sig = [c for c in ["junction_name", "signal_type", "operational_status",
                                 "green_duration_sec", "installed_date"] if c in df_sig.columns]
        show_table(df_sig[cols_sig].fillna("—"))
    else:
        st.info("No signal data.")
