"""Screen 5: Roads & Zones — browse roads, junctions, zones, analytics."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
from api_client import get

st.set_page_config(page_title="Roads & Zones — Urban Traffic", page_icon="🛣️", layout="wide")
role = st.session_state.get("role", "public")

st.title("🛣️ Roads, Junctions & Zones")
st.caption("Browse the road network and zone analytics")

tab_roads, tab_junctions, tab_zones, tab_analytics = st.tabs(
    ["🛣️ Roads", "🚦 Junctions", "🏙️ Zones", "📈 Analytics"]
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
        st.dataframe(df[cols].fillna("—"), use_container_width=True, hide_index=True)
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
        st.dataframe(df_j[cols_j].fillna("—"), use_container_width=True, hide_index=True)
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
        st.dataframe(df_z[cols_z].fillna(0), use_container_width=True, hide_index=True)
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
        st.dataframe(df_t.fillna("—"), use_container_width=True, hide_index=True)
        if "avg_vehicles" in df_t.columns and "junction_name" in df_t.columns:
            st.bar_chart(df_t.set_index("junction_name")["avg_vehicles"])
    else:
        st.info("No congestion data in last 24 hours.")
