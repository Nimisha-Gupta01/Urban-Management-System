"""Screen 4: Incidents — view, report, resolve, delete."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
from datetime import datetime
from api_client import get, post, put, delete

st.set_page_config(page_title="Incidents — Urban Traffic", page_icon="🚨", layout="wide")
role = st.session_state.get("role", "public")

st.title("🚨 Incident Management")
st.caption("Report, view, and resolve traffic incidents — ACID transaction T2 demo")

tab_view, tab_report = st.tabs(["📋 View Incidents", "📝 Report Incident"])

# ── Tab 1: View Incidents ─────────────────────────────────────────────────────
with tab_view:
    col1, col2, col3 = st.columns(3)
    with col1:
        show_open = st.checkbox("Open incidents only", value=True)
    with col2:
        sev_filter = st.selectbox("Severity", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()

    params = {"open_only": str(show_open).lower(), "limit": 100}
    if sev_filter != "All":
        params["severity"] = sev_filter

    data, err = get("/api/incidents", params=params, role=role)
    if err:
        st.error(err)
        st.stop()

    if not data:
        st.success("No incidents found.")
    else:
        df = pd.DataFrame(data)

        # Summary strip
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c2.metric("Critical", int((df["severity"] == "CRITICAL").sum()))
        c3.metric("High", int((df["severity"] == "HIGH").sum()))
        c4.metric("Medium/Low", int(df["severity"].isin(["MEDIUM","LOW"]).sum()))

        st.divider()

        for _, row in df.iterrows():
            sev_color = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(row["severity"], "⚪")
            with st.expander(f"{sev_color} [{row['severity']}] {row['incident_type']} — {row.get('road_name') or row.get('junction_name') or 'Location TBD'}"):
                col_a, col_b = st.columns(2)
                col_a.markdown(f"**ID:** {row['incident_id']}")
                col_a.markdown(f"**Type:** {row['incident_type']}")
                col_a.markdown(f"**Severity:** {row['severity']}")
                col_a.markdown(f"**Road:** {row.get('road_name') or '—'}")
                col_a.markdown(f"**Junction:** {row.get('junction_name') or '—'}")
                col_b.markdown(f"**Reported:** {row['reported_datetime']}")
                col_b.markdown(f"**Resolved:** {row.get('resolved_datetime') or 'Open'}")
                col_b.markdown(f"**Reported by:** {row.get('reported_by') or '—'}")
                col_b.markdown(f"**Description:** {row.get('description') or '—'}")

                # Resolve button (officer/admin)
                if role in ("officer", "admin") and not row.get("resolved_datetime"):
                    if st.button(f"✅ Resolve #{row['incident_id']}", key=f"resolve_{row['incident_id']}"):
                        res, err2 = put(
                            f"/api/incidents/{row['incident_id']}",
                            {"resolved_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                            role=role
                        )
                        if err2:
                            st.error(err2)
                        else:
                            st.success("Incident resolved.")
                            st.rerun()

                # Delete button (admin only)
                if role == "admin":
                    if st.button(f"🗑️ Delete #{row['incident_id']}", key=f"del_{row['incident_id']}"):
                        res, err2 = delete(f"/api/incidents/{row['incident_id']}", role=role)
                        if err2:
                            st.error(err2)
                        else:
                            st.success("Incident deleted.")
                            st.rerun()

# ── Tab 2: Report Incident ────────────────────────────────────────────────────
with tab_report:
    if role == "public":
        st.warning("⚠️ Switch to Officer or Admin role to report incidents.")
    else:
        st.subheader("Report New Incident")

        roads_data, _ = get("/api/roads", role=role)
        junctions_data, _ = get("/api/junctions", role=role)
        road_opts = {"— none —": None} | {r["road_name"]: r["road_id"] for r in (roads_data or [])}
        junc_opts = {"— none —": None} | {j["junction_name"]: j["junction_id"] for j in (junctions_data or [])}

        c1, c2 = st.columns(2)
        with c1:
            inc_type  = st.selectbox("Incident Type *", ["Accident", "Breakdown", "Roadblock", "Flooding"])
            severity  = st.selectbox("Severity *", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            road_sel  = st.selectbox("Road", list(road_opts.keys()))
        with c2:
            junc_sel  = st.selectbox("Junction", list(junc_opts.keys()))
            reported_by = st.text_input("Reported By", value="Traffic Officer")

        description = st.text_area("Description", height=80)

        if st.button("🚨 Submit Incident", type="primary"):
            payload = {
                "incident_type": inc_type,
                "severity": severity,
                "description": description or None,
                "road_id": road_opts.get(road_sel),
                "junction_id": junc_opts.get(junc_sel),
                "reported_by": reported_by or "API",
            }
            result, err = post("/api/incidents", payload, role=role)
            if err:
                st.error(f"Failed: {err}")
            else:
                st.success(f"✅ Incident reported! ID: {result.get('incident_id')}")
