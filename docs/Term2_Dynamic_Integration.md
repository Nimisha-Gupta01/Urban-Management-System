# Term 2 — Making the System Dynamic (Real-World Integration)
### Handoff document for teammate | SESAP ZC337

This document describes what is needed to evolve the current prototype from
**simulated/seeded static data** into a **live, real-world dynamic system**.

---

## Current State (what exists)

- PostgreSQL database with 13+ tables, triggers, views, stored procedures
- FastAPI backend with CRUD endpoints
- Streamlit UI with dashboard, map, traffic observations, incidents
- All traffic data is **manually entered or seeded** — nothing updates automatically

---

## What Needs to Become Dynamic

### 1. Real-Time Traffic Data Ingestion

**Problem:** Traffic observations currently come from manual form submissions only.

**What's needed in real life:**

| Source | Description | Integration needed |
|---|---|---|
| **Traffic sensors** (loop detectors, radar) | Embedded in roads, count vehicles and measure speed every 30–60 sec | Sensor pushes data to a REST endpoint (`POST /api/traffic`) via MQTT or HTTP |
| **CCTV / traffic cameras** | Video feeds at junctions processed by computer vision (YOLO/OpenCV) to count vehicles | ML pipeline outputs vehicle count + speed → POST to API |
| **GPS probe data** | Anonymised GPS from vehicles/apps (like Google Maps or Ola) aggregated per road segment | Batch job every 5 min pulls from fleet APIs, aggregates, inserts |
| **Manual officer entry** | Already implemented in UI | Done ✓ |

**API endpoint already exists:** `POST /api/traffic` — just needs a real caller instead of manual form.

**Suggested approach for Term 2:**
- Write a Python simulator script (`data/simulator.py`) that fires POST requests every 30 seconds with randomised-but-realistic values, simulating sensors
- Or integrate with a free public traffic API (e.g. TomTom Traffic API, HERE Maps) for Bengaluru roads

---

### 2. Automatic Junction Congestion Updates

**Problem:** `junction.congestion_status` is updated by a PostgreSQL trigger after each observation INSERT — this is already implemented. But it only updates when a new observation arrives.

**What's needed in real life:**
- A **scheduled job** (cron or Celery beat) that runs every 60 seconds, checks if any junction has had no observation in the last 10 minutes, and resets its status to `UNKNOWN`
- A **decay function**: congestion level should reduce over time if no new high-vehicle-count observations arrive

**Files to create:**
- `app/scheduler.py` — APScheduler or Celery beat task
- New SQL function: `fn_decay_congestion_status()`

---

### 3. Real Incident Reporting

**Problem:** Incidents are manually entered by officers through the UI.

**What's needed in real life:**

| Source | Description |
|---|---|
| **Police/traffic authority API** | Cities like Bengaluru have BMLTA / BBMP traffic management APIs — incidents can be pulled |
| **Citizen reporting app** | A mobile form where citizens report accidents, flooding, roadblocks |
| **Social media scraping** | Twitter/X keyword monitoring for traffic keywords + Bengaluru junction names |
| **Automated camera detection** | If camera detects stationary vehicles > 5 min → auto-raise incident |

**Suggested approach for Term 2:**
- Add a public `POST /api/incidents/report` endpoint (no auth required) that citizens can call
- Build a simple mobile-friendly HTML form (single page, no login) that posts to this endpoint

---

### 4. Sensor Table Population

**Problem:** The `Sensor` table exists in the schema but is never populated or read.

**What's needed in real life:**
- Each physical sensor has a unique ID, is registered in the Sensor table
- Sensor sends heartbeat + reading every N seconds
- A new table `Sensor_Reading` (time-series) should store raw sensor output
- `Traffic_Observation` is then derived/aggregated from sensor readings

**New table needed:**
```sql
CREATE TABLE Sensor_Reading (
    reading_id   SERIAL PRIMARY KEY,
    sensor_id    INTEGER REFERENCES Sensor(sensor_id),
    read_time    TIMESTAMP DEFAULT NOW(),
    vehicle_count INTEGER,
    avg_speed    REAL,
    raw_payload  JSONB   -- store full sensor JSON for debugging
);
```

---

### 5. Traffic Signal Integration

**Problem:** `Traffic_Signal` table stores signal config but signals are never actually controlled by the system.

**What's needed in real life:**
- Adaptive signal control: when a junction shows `SEVERE` congestion, automatically extend green phase on the congested approach
- Signal controller APIs (most modern signals support REST or SNMP)

**Suggested approach for Term 2:**
- Add `POST /api/signals/{signal_id}/override` endpoint that updates `green_duration_sec`
- Write a rule engine: if `congestion_status = SEVERE` for junction → call signal override API
- This demonstrates **closed-loop control** (observe → decide → act)

---

### 6. Spatial / GIS Extension (Term 2 Multimodal)

**Problem:** Junctions have lat/lon but no spatial queries are possible.

**What's needed:**
- Enable PostGIS extension in PostgreSQL
- Change `latitude/longitude` columns to `PostGIS GEOGRAPHY POINT`
- Add spatial queries: "find all junctions within 2km of a given point", "find the nearest available hospital to an incident"
- Add road geometry (LineString) so roads are rendered as actual paths on the map

**Steps:**
```sql
CREATE EXTENSION postgis;
ALTER TABLE Junction ADD COLUMN geom GEOGRAPHY(POINT, 4326);
UPDATE Junction SET geom = ST_MakePoint(longitude, latitude);
```

---

### 7. Time-Series Analytics

**Problem:** Historical traffic data accumulates but no trend analysis exists.

**What's needed:**
- Weekly/monthly congestion heatmaps per junction
- Prediction: "based on last 4 weeks, Tuesday 8–9am at Silk Board is always SEVERE"
- TimescaleDB extension (time-series optimised PostgreSQL) for hypertables on `Traffic_Observation`

---

### 8. Automated Alerts / Notifications

**What's needed:**
- When a junction stays `SEVERE` for > 15 minutes → send alert email/SMS to traffic authority
- When an incident is reported near a school zone → auto-escalate severity to CRITICAL

**Tools:** Twilio (SMS), SendGrid (email), or WhatsApp Business API

---

## Suggested Term 2 Roadmap

| Week | Task |
|---|---|
| 1–2 | Write data simulator script (`simulator.py`) — auto-POST observations every 30s |
| 3–4 | Enable PostGIS, migrate lat/lon to geometry, add spatial queries to API |
| 5–6 | Build Sensor_Reading time-series table + TimescaleDB hypertable |
| 7–8 | Adaptive signal control rule engine |
| 9–10 | Citizen incident reporting endpoint + simple mobile form |
| 11–12 | Analytics dashboard: weekly heatmap, peak prediction |

---

## Files Your Teammate Should Focus On

| File | What to add |
|---|---|
| `app/main.py` | New endpoints for sensor ingestion, signal override, public incident report |
| `sql/schema.sql` | `Sensor_Reading` table, PostGIS columns |
| `data/simulator.py` | **Create this** — traffic sensor simulator |
| `streamlit_app/pages/` | New page for heatmap / prediction analytics |
| `docker-compose.yml` | Add TimescaleDB or PostGIS-enabled postgres image |

---

## Contact / Handoff Notes

- All existing API endpoints are documented at `http://localhost:8000/docs` (Swagger UI)
- Database schema is in `sql/schema.sql`
- ER diagram is in `docs/ER_Diagram.drawio` (open at app.diagrams.net)
- To run locally: see `README.md`
