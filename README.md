# Urban Road & Real-Time Traffic Management System
### BITS Pilani WILP | SESAP ZC337 — Database Systems and Applications
### Team: Nimisha Gupta (I578445) · Fasi Ahmed Khan (I578459)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL 16 |
| Backend API | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| Containerisation | Docker + Docker Compose |
| Modelling | draw.io |

---

## Project Structure

```
Urban_Traffic_Management_System/
├── docker-compose.yml          ← runs all 3 services
├── Dockerfile                  ← shared image for API + Streamlit
├── requirements.txt
├── init_db.py                  ← seeds schema + sample data on first run
├── sql/
│   ├── schema.sql              ← CREATE TABLE statements (PostgreSQL)
│   ├── queries.sql             ← analytical queries
│   └── triggers.sql            ← triggers, views, stored procedures
├── app/
│   └── main.py                 ← FastAPI backend (all /api/* routes)
├── streamlit_app/
│   ├── Home.py                 ← landing page (KPIs + feature cards)
│   ├── api_client.py           ← shared HTTP client, theme, table helper
│   └── pages/
│       ├── 1_Dashboard.py      ← live map + junction status
│       ├── 2_Traffic.py        ← filter & search observations
│       ├── 3_Add_Observation.py← POST new traffic observation
│       ├── 4_Incidents.py      ← incident management
│       └── 5_Roads_Zones.py    ← road network & zone analytics
└── docs/
    ├── SRS.md
    ├── ER_Diagram.drawio
    └── ...
```

---

## Running the Application

### Option 1 — Docker (recommended, one command)

**Prerequisites:** Docker Desktop installed and running.

```bash
# Clone / navigate to the project folder
cd Urban_Traffic_Management_System

# Build and start all services (first run takes ~2 min to build)
docker compose up --build

# Subsequent runs (no rebuild needed)
docker compose up
```

Once running, open:

| Service | URL |
|---|---|
| **Streamlit UI** | http://localhost:8501 |
| **FastAPI docs** | http://localhost:8000/docs |
| **PostgreSQL** | localhost:5432 (user: `traffic_user`, db: `traffic_db`, pass: `traffic_pass`) |

To stop:
```bash
docker compose down
```

To stop and delete all data (wipe the database):
```bash
docker compose down -v
```

---

### Option 2 — Local (without Docker)

**Prerequisites:** Python 3.11+, PostgreSQL 16 running locally.

#### 1. Create the database

```bash
psql -U postgres -c "CREATE USER traffic_user WITH PASSWORD 'traffic_pass';"
psql -U postgres -c "CREATE DATABASE traffic_db OWNER traffic_user;"
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Set environment variables

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=traffic_db
export PGUSER=traffic_user
export PGPASSWORD=traffic_pass
```

#### 4. Seed the database

```bash
python init_db.py
```

#### 5. Start the FastAPI backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 6. Start the Streamlit UI (new terminal)

```bash
export API_BASE=http://localhost:8000
streamlit run streamlit_app/Home.py --server.port 8501
```

Open http://localhost:8501 in your browser.

---

## UI Walkthrough

### Role selector (sidebar)
Switch between **Public / Officer / Admin** to simulate role-based access:
- **Public** — read-only (Dashboard, Traffic, Roads & Zones)
- **Officer** — can add traffic observations and manage incidents
- **Admin** — full access including delete

### Pages

| Page | What it shows |
|---|---|
| **Home** | Live city KPIs (observations, avg speed, congestion count) + quick-nav cards |
| **Dashboard** | Interactive Bengaluru map with colour-coded junctions, zone summary, open incidents chart |
| **Traffic Data** | Filter observations by zone / junction / congestion level / time window; peak-hours chart |
| **Add Observation** | Submit a new traffic observation (Officer/Admin only) — demonstrates ACID transaction T1 + PostgreSQL trigger |
| **Incidents** | View, filter, update, and resolve incidents (Admin can delete) |
| **Roads & Zones** | Browse road network, junctions, zone analytics, top-5 congested junctions chart |

### Map legend
| Colour | Congestion level |
|---|---|
| 🟢 Green | LOW |
| 🔵 Blue | MODERATE |
| 🟠 Orange | HIGH |
| 🔴 Red | SEVERE |
| ⚫ Grey | No data |

---

## Key Database Features Demonstrated

| Feature | Where |
|---|---|
| ACID Transaction (T1) | POST /api/traffic → inserts observation atomically |
| PostgreSQL Trigger | After INSERT on traffic_observation → updates junction congestion_status |
| Views | v_junction_live_status, v_zone_summary used by dashboard API |
| Stored Procedure | sp_resolve_incident — updates incident + logs to audit table |
| Audit Log | Incident_Audit table populated by trigger on severity change |
| Role-Based Access | X-User-Role header → API enforces read/write/delete permissions |
| Indexes | On junction_id, road_id, observation_time for fast filtering |

---

## Team Responsibilities

| Area | Nimisha | Fasi |
|---|---|---|
| SRS Document | owns | reviews |
| ER / EER Diagram | owns | contributes |
| Normalization (FDs, BCNF) | owns | reviews |
| PostgreSQL Schema | shared | shared |
| Data Seeding | — | owns |
| SQL Queries | shared | shared |
| Triggers / Views | owns | — |
| FastAPI Backend | shared | shared |
| Streamlit UI | owns | — |
| Transactions + Concurrency | owns | — |
| Docker Setup | — | owns |
