"""Screen 6: Report an Incident — public citizen form, no login required."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
from api_client import get, apply_light_theme, icon

st.set_page_config(page_title="Report Incident — Urban Traffic", page_icon="🚨", layout="centered")
apply_light_theme()

st.markdown(
    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:0.2rem;">'
    f'{icon("report_problem", size="lg", color="#e53935")}'
    f'<span style="font-size:1.8rem;font-weight:700;color:#1a1a2e;">Report a Traffic Incident</span>'
    f'</div>',
    unsafe_allow_html=True,
)
st.caption("Anyone can report — no login required. Officers will review and escalate if needed.")

junctions_data, _ = get("/api/junctions", role="public")
junction_opts = {"— Not sure / Not applicable —": None}
if junctions_data:
    junction_opts |= {j["junction_name"]: j["junction_id"] for j in junctions_data}

roads_data, _ = get("/api/roads", role="public")
road_opts = {"— Not sure / Not applicable —": None}
if roads_data:
    road_opts |= {r["road_name"]: r["road_id"] for r in roads_data}

with st.form("citizen_report"):
    st.subheader("What happened?")

    incident_type = st.selectbox(
        "Incident Type *",
        ["Accident", "Breakdown", "Roadblock", "Flooding"],
    )

    description = st.text_area(
        "Description",
        placeholder="Briefly describe what you saw — e.g. 'Two vehicles collided near the signal'",
        max_chars=500,
    )

    st.subheader("Where?")
    sel_junction = st.selectbox("Nearest Junction", list(junction_opts.keys()))
    sel_road     = st.selectbox("Nearest Road",     list(road_opts.keys()))

    submitted = st.form_submit_button("📤 Submit Report", use_container_width=True, type="primary")

if submitted:
    payload = {
        "incident_type": incident_type,
        "description":   description or None,
        "junction_id":   junction_opts[sel_junction],
        "road_id":       road_opts[sel_road],
    }

    from api_client import post as api_post
    resp_data, err = api_post("/api/incidents/report", payload, role="public")
    if err:
        st.error(f"Submission failed: {err}")
    else:
        st.success(f"Thank you! Your report has been submitted (ID: {resp_data.get('incident_id')}). "
                   f"Traffic officers have been notified.")
