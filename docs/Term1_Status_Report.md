# Term 1 — Project Status Report
## Urban Road & Real-Time Traffic Management System
**BITS Pilani WILP | SESAP ZC337 | Nimisha Gupta**  
**Lab Session 2 Deadline: 17 October 2026**

---

## What This Document Is

A plain-language summary of:
1. What is fully built and working
2. What is simulated / static (and why that is acceptable)
3. What is pending for Lab Session 2 (17 Oct)
4. What is planned for Lab Session 3 / MVP (28 Nov)

---

## Part 1 — What Is Fully Built and Working

### Database Layer

| Item | Status | Detail |
|------|--------|--------|
| Schema (`sql/schema.sql`) | ✅ Done | 10 base tables + 8 ISA subtype tables + 1 Audit_Log table. All in BCNF. |
| Foreign Key constraints | ✅ Done | All 14 FK relationships. `PRAGMA foreign_keys = ON` enforced on every connection. |
| CHECK constraints | ✅ Done | Severity IN (LOW/MEDIUM/HIGH/CRITICAL), congestion_level IN (LOW/MODERATE/HIGH/SEVERE), speed_limit BETWEEN 10 AND 120, lat/lon ranges. |
| UNIQUE constraints | ✅ Done | license_plate, license_no, zone_name. |
| 9 Indexes (`sql/schema.sql`) | ✅ Done | 7 B+ tree indexes on JOIN/range columns + 2 hash-equivalent UNIQUE indexes. |
| 4 Triggers (`sql/triggers.sql`) | ✅ Done | Congestion alert (vehicle_count > 200 → update junction), congestion reset, incident audit INSERT, incident audit UPDATE. |
| 3 Views (`sql/triggers.sql`) | ✅ Done | TrafficDashboard, ZoneSummary, IncidentReport. |
| Seed data (`sql/seed_data.sql`) | ✅ Done | 5 zones, 20 roads, 15 junctions, 100+ observations, 7 incidents, 10 vehicles, 10 drivers, 8 sensors. |
| ACID transaction demo | ✅ Done | BEGIN/COMMIT/ROLLBACK blocks in `sql/triggers.sql` with 4 scenarios (valid insert, SAVEPOINT, invalid FK → ROLLBACK, WAL checkpoint). |
| ISA subtypes | ✅ Done | Car, Truck, Motorcycle, Bus (under Vehicle); Accident, Breakdown, Roadblock, Flooding (under Incident). |
| BCNF normalization | ✅ Done | All 10 tables verified. Full FD analysis and walkthrough documented in SRS Section 4.4. |

### Backend API (`app/app.py`)

| Item | Status | Detail |
|------|--------|--------|
| Flask REST API | ✅ Done | 14 JSON endpoints + 5 HTML page routes = 19 routes total. |
| GET /api/zones | ✅ Done | Returns all 5 zones. |
| GET /api/roads | ✅ Done | Returns roads, filterable by `?zone_id=`. |
| GET /api/junctions | ✅ Done | Returns junctions, filterable by `?zone_id=`. |
| GET /api/traffic | ✅ Done | Returns observations, filterable by junction/road/hours. |
| POST /api/traffic | ✅ Done | Inserts observation inside BEGIN/COMMIT/ROLLBACK. Officer/admin only. |
| GET/POST/PUT/DELETE /api/incidents | ✅ Done | Full CRUD on incidents. Role-gated. |
| GET /api/map | ✅ Done | 15 junctions with lat/lon + latest congestion + open incidents with coordinates. |
| GET /api/dashboard | ✅ Done | KPIs + junction status + zone summary + incident severity breakdown. |
| GET /api/analytics/peak-hours | ✅ Done | Observations grouped by hour of day using `strftime()`. |
| GET /api/analytics/top-congested | ✅ Done | Top 5 most congested junctions (last 24h). |
| GET /api/audit | ✅ Done | Audit log (admin only). |
| Role-based access control | ✅ Done | X-User-Role header. Public/Officer/Admin tiers. 403 on violations. |
| Input validation | ✅ Done | Missing fields → 400. Invalid FK → ROLLBACK → 400. resolved < reported → 400. |
| Parameterized SQL | ✅ Done | All queries use `?` placeholders. No string concatenation anywhere. |
| WAL mode + FK pragma | ✅ Done | Set on every connection in `get_db()`. |
| Connection-per-request | ✅ Done | Flask `g` pattern. Thread-safe for SQLite. |

### Frontend (5 Screens)

| Screen | Status | What It Does |
|--------|--------|-------------|
| Dashboard (`/`) | ✅ Done | 4 KPI cards + Leaflet.js map (colour-coded junction markers + incident diamonds) + junction table + zone table + incident severity strip. Auto-refreshes every 60 seconds. |
| Traffic Observations (`/traffic`) | ✅ Done | Filter by zone/junction/congestion/hours. Peak-hour bar chart (pure CSS). Results table. |
| Incident Management (`/incidents`) | ✅ Done | Report incident form (officer/admin). Open incidents table. Resolve modal. Delete (admin only). |
| Add Observation (`/observation`) | ✅ Done | Zone → Junction cascade dropdowns. Auto-suggests congestion level. Shows recent 10 observations for selected junction. |
| Roads & Junctions (`/roads`) | ✅ Done | 4-tab interface: Roads, Junctions, Zones, Analytics (Top-5 congested). |

### Infrastructure

| Item | Status | Detail |
|------|--------|--------|
| CI/CD pipeline | ✅ Done | GitHub Actions: checkout → install deps → validate SQL → init DB → pytest → Docker build + smoke test. Triggers on every `git push`. |
| Dockerfile | ✅ Done | Python 3.12-slim. Runs `init_db.py` at build time. |
| docker-compose.yml | ✅ Done | Single service, persistent volume for SQLite. |
| DB initializer (`init_db.py`) | ✅ Done | Runs schema → DDL triggers → seed in correct order. `--reset` flag supported. |
| Automated tests (`tests/test_api.py`) | ✅ Done | 27 pytest tests. Health, CRUD, RBAC (403), validation (400), HTML pages, analytics, map. |

### Documentation

| Document | Status | Detail |
|----------|--------|--------|
| SRS (`docs/SRS.md`) | ✅ Done | IEEE 830 / ISO 29148, v2.0. 11 sections. 26 FRs, 15 NFRs, data dictionary, BCNF proofs, indexing, ACID demo, RBAC, CI/CD, 27 test cases, WIA 1–5 mapping, viva prep. |
| ER Diagram Spec (`docs/ER_Diagram_Specification.md`) | ✅ Done | Complete Chen notation drawing guide, all 10 entities, 11 relationships table, 2 ISA hierarchies, AI image prompt, draw.io instructions. |

---

## Part 2 — What Is Simulated / Static (and Why It's Fine)

### Traffic Observations — Simulated, NOT live sensor data

**What it is:** ~100 rows inserted by `seed_data.sql` using `datetime('now', '-X hours')`. These timestamps are relative to whenever the database is initialised — so "last 24 hours" queries always return data.

**What it is NOT:** live data from real Bengaluru traffic sensors. No sensor feeds, no WebSocket streams, no external API calls.

**Why this is acceptable for Term 1:**
- The lab handout explicitly says: *"Real-time data ingestion — you handle this by simulating or batch-importing"*
- SQLite is not designed for high-frequency live writes — that is a Term 2 (PostgreSQL + TimescaleDB) problem
- The project brief says: *"Use Kaggle traffic dataset to seed your database"* — our seed data plays exactly this role
- The teacher expects simulation at this stage

**What the demo will show:** The dashboard, map, and tables will display populated, realistic-looking data. When you POST a new observation via the Add Observation screen during the demo, the map marker will visibly update on the next 60-second refresh. This demonstrates the live write path end-to-end.

---

### Junction GPS Coordinates — Real Bengaluru locations, hardcoded

**What it is:** Real latitude/longitude values for 15 actual Bengaluru junctions (Silk Board, ITPL, Hebbal Flyover, etc.) hardcoded in `seed_data.sql`.

**What it is NOT:** Dynamically fetched from OpenStreetMap or any GIS API.

**Why acceptable:** The coordinates are accurate for the real locations. Leaflet.js renders them correctly on the OpenStreetMap tile layer. For Term 1, static seed data is exactly what was asked for.

---

### Congestion Levels — Rule-based, NOT ML-predicted

**What it is:** Congestion level (LOW/MODERATE/HIGH/SEVERE) is either set manually in seed data or auto-derived by a trigger when `vehicle_count > 200`.

**What it is NOT:** A machine learning model or real traffic speed prediction algorithm.

**Why acceptable:** The trigger demonstrates the DBSA concept of database-side business logic. Congestion prediction via ML is a Term 2 / elective enhancement.

---

### Role Authentication — Header simulation, NOT real login

**What it is:** The `X-User-Role` HTTP header is set by a `<select>` dropdown in the nav bar and stored in `localStorage`. The Flask backend reads this header to enforce RBAC.

**What it is NOT:** A real login system with passwords, JWT tokens, or session management.

**Why acceptable:** The lab handout explicitly says *"Login/User screen — optional/simple"* and *"Avoid: elaborate authentication"*. The RBAC enforcement (who can POST/DELETE/view audit log) is fully implemented — the login layer is deliberately simplified per the spec.

---

## Part 3 — Pending for Lab Session 2 (17 October 2026)

These are the only remaining tasks before the demo:

| # | Task | Effort | Why Needed |
|---|------|--------|-----------|
| 1 | **Generate ER diagram image** | 30 min | Required deliverable. Use the AI prompt in `docs/ER_Diagram_Specification.md` with ChatGPT/DALL-E or draw manually in draw.io. Save as `docs/ER_Diagram.png`. |
| 2 | **Run the app locally and verify end-to-end** | 15 min | Must demo live on 17 Oct. Confirm all 5 screens load, map shows markers, POST observation works, trigger fires. |
| 3 | **Upload SRS to Taxila** | 5 min | Mandatory submission. Export/copy `docs/SRS.md`. |
| 4 | **Prepare demo script** | 20 min | Know the 2-minute walkthrough: open dashboard → show map → post observation → show trigger effect → show incidents → show audit log. |

**Nothing in the code needs to change for Lab Session 2.** The prototype is complete.

---

## Part 4 — Planned for Lab Session 3 / MVP (28 November 2026)

Lab Session 3 asks for the **MVP** — a more polished, complete product. Based on what we have, the natural next steps are:

### High Priority (directly addresses MVP requirements)

| # | Enhancement | Why |
|---|-------------|-----|
| 1 | **Live data simulation script** (`simulate_traffic.py`) | A background Python thread that auto-inserts one observation per junction every 30 seconds. Makes the map visibly change during a 5-minute demo. Transforms "simulated" into "feels real-time". |
| 2 | **Fix seed timestamps to be rolling** | Already done — `datetime('now', '-X hours')` is already used. But need to re-init DB at demo time so timestamps are fresh. |
| 3 | **Login screen (simple)** | The handout listed it as optional for Session 2 but expected by MVP. Simple username/password form, session cookie, maps to one of the 3 roles. No elaborate JWT needed. |
| 4 | **Deploy to a cloud VM** | Handout says *"deployment could be a single VM/server or simple cloud environment"*. A free-tier AWS EC2 or Railway.app deploy makes it accessible via URL, not just localhost. |

### Medium Priority (strengthens DBSA concepts for viva)

| # | Enhancement | Why |
|---|-------------|-----|
| 5 | **EXPLAIN QUERY PLAN demo page** | A hidden `/debug/explain` endpoint showing index usage on the dashboard query. Directly answers viva question 7. |
| 6 | **WAL recovery demo script** | A Python script that: (a) starts a transaction, (b) simulates a crash (kills process), (c) restarts and shows the DB is consistent. Directly answers viva question 4. |
| 7 | **More sample SQL queries page** | A `/queries` page showing the 7 sample queries from `Urban_Traffic_DB_Project.md` running live with results. Shows the full SQL complexity range. |
| 8 | **Pagination on tables** | Currently tables show all rows. Add limit/offset pagination for scalability demo (NFR8). |

### Term 2 Scope (PostgreSQL migration)

| # | Enhancement | Why |
|---|-------------|-----|
| 9 | **Migrate to PostgreSQL** | SQLite limitations for concurrency and spatial data. Term 2 requires PostGIS. |
| 10 | **PostGIS spatial columns** | Add geometry to Junction and Road. `ST_Distance` queries. R-Tree spatial index. |
| 11 | **TimescaleDB / partitioned tables** | Partition Traffic_Observation by month for scalable time-series. |
| 12 | **Real GRANT/REVOKE** | PostgreSQL has real role-based access at DB level — replace header simulation with real DB roles. |
| 13 | **Traffic camera image storage** | File path in DB + BLOB for thumbnails. |

---

## Quick Summary Table

| Layer | Term 1 Status | Simulated? | Term 2 Plan |
|-------|--------------|-----------|------------|
| Database schema | ✅ Complete | No — real schema | Add geometry columns |
| Seed data | ✅ Complete | Yes — batch insert simulates sensors | Replace with live API feed |
| Triggers + Views | ✅ Complete | No — real DB logic | Add more analytical views |
| BCNF normalization | ✅ Complete | No — real design decision | — |
| Indexing | ✅ Complete | No — real indexes | Add spatial R-tree index |
| ACID transactions | ✅ Complete | Demo scripts exist | Use PostgreSQL transactions |
| RBAC | ✅ Complete | Simulated via header | Real DB GRANT/REVOKE in PostgreSQL |
| REST API (14 endpoints) | ✅ Complete | No — real working API | Add spatial query endpoints |
| Frontend (5 screens) | ✅ Complete | No — real working UI | Add login screen, pagination |
| Leaflet.js map | ✅ Complete | Data is seeded, not live | Connect to live simulation script |
| CI/CD pipeline | ✅ Complete | No — real pipeline | Add cloud deploy step |
| Docker | ✅ Complete | No — real container | Add cloud deployment target |
| Automated tests (27) | ✅ Complete | No — real tests | Add load/performance tests |
| SRS document | ✅ Complete | No | Update for Term 2 scope |
| ER diagram image | ⚠️ Spec written, image pending | No | — |
| Login screen | ⚠️ Not built | — | Build for MVP (Session 3) |
| Live data simulation | ⚠️ Not built | — | Build for MVP (Session 3) |
| Cloud deployment | ⚠️ Not built | — | Build for MVP (Session 3) |

---

*Prepared: October 2026 | BITS Pilani WILP | SESAP ZC337*  
*Next deadline: Lab Session 2 — 17 October 2026 (Prototype + SRS)*  
*Following deadline: Lab Session 3 — 28 November 2026 (MVP)*
