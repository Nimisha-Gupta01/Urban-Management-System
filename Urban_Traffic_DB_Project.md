# Urban Road & Real-Time Traffic Information and Management Database
### BITS Pilani WILP | SESAP ZC337 – Database Systems and Applications
### Capstone Project – Term 1 & Term 2

---

## Quick Verdict: Should You Pick This?

**Yes — this is your best option among the 3.** Here's why in one line:  
Traffic data is publicly available, spatially rich, technically demanding, directly maps to every DBMS concept in your syllabus, and produces a portfolio project that looks impressive for both IT and MTech profiles.

The other two are covered further below with honest trade-offs.

---

## 1. Complexity Assessment

### Overall Complexity: Medium-High (7/10)

| Dimension | Rating | Why |
|---|---|---|
| Schema Design | Medium | 8–10 entities, moderate relationships |
| Data Sourcing | Easy–Medium | Free public APIs exist (see Section 3) |
| SQL Complexity | High | Spatial joins, time-series aggregations, window functions |
| Term 2 Extension | High | GIS/spatial data, sensor streams, image storage |
| 2-Person Team Fit | Excellent | Clean split: one person per domain |

### What makes it hard
- Real-time data ingestion (you handle this by simulating or batch-importing)
- Term 2 spatial data (PostGIS, R-Tree indexing) — new territory if you haven't done GIS
- Keeping the schema normalized while handling high-frequency sensor data

### What makes it manageable
- Term 1 is pure relational — no spatial needed yet
- You can use a **single Indian city** (e.g., Bangalore/Mumbai) and limit scope
- Free datasets exist from government open data portals
- SQLite for Term 1 is fully sufficient (per lab instructions)

---

## 2. Is 2 People Enough?

**Yes — cleanly split into two workstreams:**

| Person | Owns |
|---|---|
| Person A | Schema design, ER diagram, normalization, SQL queries, indexing |
| Person B | Data collection/cleaning, application prototype, transactions/security |

Both contribute to SRS, viva, and documentation. 2 is actually the ideal team size for this — any more people and coordination overhead increases without proportional benefit.

**Time estimate per person (Term 1):** ~8–10 hours/week across 8 weeks = 64–80 hours total.

---

## 3. Data Sources — Where to Get Real Data

### Free & Publicly Available Sources

| Source | What You Get | Link Type |
|---|---|---|
| **data.gov.in** | Indian road network, accident data, traffic stats | Government open data portal |
| **OpenStreetMap (OSM)** | Road network, junction data, GIS coordinates | Free download via Overpass API |
| **NCRB (National Crime Records Bureau)** | Road accident data city-wise | Annual PDF reports, extractable |
| **iNATDATAHUB / MoRTH** | Ministry of Road Transport accident statistics | PDF + CSV downloads |
| **Kaggle** | Multiple traffic datasets (US/India) | Ready-to-use CSV |
| **HERE Maps / TomTom (free tier)** | Traffic flow data via API (limited calls) | REST API |
| **Google Maps Platform** | Traffic conditions (free $200/month credit) | REST API |
| **SUMO (Simulation)** | Simulate your own urban traffic | Open source traffic simulator |

### Recommended approach for Term 1
Use **Kaggle traffic dataset** (e.g., "Bengaluru Traffic Dataset" or "India Road Accidents") to seed your database. This gives you clean CSV data you can directly import into SQLite. No API dependency, no rate limits, works offline.

### For Term 2
Use **OpenStreetMap** for GIS road network data + simulated sensor readings (Python script generating time-series INSERT statements).

---

## 4. End-to-End Project Flow

```
PHASE 0 (Week 1–2): SRS & Problem Definition
    └── Define scope: Pick one city (e.g., Bengaluru)
    └── Identify users: Traffic Police, Commuters, City Planners, Emergency Services
    └── List functional requirements (30+ use cases)
    └── Document non-functional requirements (performance, concurrency, security)

PHASE 1 (Week 2–3): Conceptual Design
    └── Draw ER/EER Diagram
    └── Entities: Road, Junction, Vehicle, Driver, TrafficSignal,
                  Incident, TrafficObservation, Sensor, Zone
    └── Relationships + cardinalities
    └── Specializations (e.g., Vehicle → Car/Truck/Bike)

PHASE 2 (Week 3–4): Logical Design
    └── ER → Relational Mapping (all 7 mapping rules)
    └── Define all tables, primary keys, foreign keys
    └── Apply Normalization up to BCNF
    └── Functional dependency analysis
    └── Lossless join + dependency preserving decomposition check

PHASE 3 (Week 4–5): Physical Design
    └── Implement schema in SQLite
    └── Choose file organization strategy
    └── Design indexes (B+ Tree on junction_id, timestamp)
    └── Hashing strategy for vehicle lookup by number plate

PHASE 4 (Week 5–6): Data Population & SQL
    └── Import real dataset (Kaggle CSV → SQLite)
    └── Write 20+ SQL queries covering all syllabus topics
    └── Triggers, stored procedures, views
    └── Concurrency scenarios (two updates to same junction)

PHASE 5 (Week 6–7): Application Prototype
    └── Simple web app or Python CLI/Streamlit dashboard
    └── CRUD operations + query interface
    └── Transaction management (ACID demonstration)
    └── Security: access control, roles (Admin vs ReadOnly)

PHASE 6 (Week 7–8): Optimization & Hardening
    └── Query execution plans
    └── Index effectiveness analysis
    └── Recovery scenario (log-based, checkpoint demo)
    └── Final SRS documentation

--- TERM 1 SUBMISSION ---

TERM 2 EXTENSION:
    └── Add spatial columns (lat/long → PostGIS geometry)
    └── R-Tree spatial indexing
    └── Store traffic camera images (BLOB / file path references)
    └── Time-series sensor data (sliding window queries)
    └── Map visualization (Leaflet.js / Folium)
```

---

## 5. Entity-Relationship Overview

### Core Entities (Term 1)

```
ZONE
  zone_id (PK), zone_name, city, area_sqkm, zone_type

ROAD
  road_id (PK), road_name, road_type, length_km, num_lanes,
  speed_limit, zone_id (FK), surface_type, direction_type

JUNCTION
  junction_id (PK), junction_name, junction_type,
  latitude, longitude, zone_id (FK), signal_controlled

ROAD_JUNCTION (junction-road M:N)
  road_id (FK), junction_id (FK), position_type

TRAFFIC_SIGNAL
  signal_id (PK), junction_id (FK), signal_type,
  installed_date, operational_status, green_duration_sec

VEHICLE
  vehicle_id (PK), license_plate (UNIQUE), vehicle_type,
  make, model, year, registered_state, owner_id (FK)

DRIVER (OWNER)
  driver_id (PK), name, license_no, dob, contact, address

INCIDENT
  incident_id (PK), incident_type, severity, description,
  reported_datetime, resolved_datetime, road_id (FK),
  junction_id (FK), vehicle_id (FK), reported_by

TRAFFIC_OBSERVATION
  obs_id (PK), junction_id (FK), road_id (FK),
  observation_time (DATETIME), vehicle_count,
  avg_speed_kmph, congestion_level, weather_condition,
  data_source (sensor/manual/camera)

SENSOR
  sensor_id (PK), sensor_type, junction_id (FK),
  installation_date, status, last_reading_time
```

### Key Relationships
- A ROAD connects multiple JUNCTIONs (M:N via ROAD_JUNCTION)
- A JUNCTION can have multiple TRAFFIC_SIGNALs
- An INCIDENT involves one ROAD, one JUNCTION (nullable), one VEHICLE (nullable)
- A TRAFFIC_OBSERVATION is recorded at a JUNCTION for a ROAD segment
- A SENSOR is installed at a JUNCTION

---

## 6. DBMS Syllabus Coverage Map

This project covers **every single module** in your SESAP ZC337 syllabus:

| Syllabus Module | How This Project Covers It | Marks Relevance |
|---|---|---|
| **M1: DBMS Concepts** | Three-schema architecture for traffic system | Foundation |
| **M2: ER Modeling** | 10-entity ER diagram with ISA, aggregation | Direct deliverable |
| **M2: Relational Model** | Full schema with all 7 mapping rules | Direct deliverable |
| **M3: Relational Algebra** | Query all junctions with congestion > threshold | Homework |
| **M3: SQL** | 20+ queries: joins, groupby, nested, views, triggers | Lab + Assignment |
| **M4: Normalization** | TrafficObservation table demonstrates 3NF/BCNF | Direct deliverable |
| **M5: Indexing** | B+ Tree on (junction_id, timestamp); hash on license_plate | Work-integrated Activity 3 |
| **M5: Hashing** | Static hash on license_plate for vehicle lookup | Work-integrated Activity 3 |
| **M5: Storage** | File organization for high-frequency sensor inserts | Work-integrated Activity 3 |
| **M6: Transactions** | Concurrent signal updates, ACID demonstration | Work-integrated Activity 4 |
| **M6: Concurrency** | Two-phase locking for incident updates | Work-integrated Activity 4 |
| **M6: Recovery** | Log-based recovery after simulated crash | Work-integrated Activity 4 |
| **M7: Security** | Role-based access: Admin, TrafficOfficer, Public | Work-integrated Activity 5 |
| **M8: Query Optimization** | EXPLAIN on spatial/temporal queries | Work-integrated |
| **M8: NoSQL (if covered)** | Sensor data as document store (Term 2) | Extra credit |

**Verdict: 100% syllabus coverage. No module is left untouched.**

---

## 7. Sample SQL Queries (Showing Complexity Range)

```sql
-- Simple: All roads in a zone with speed limit > 60
SELECT r.road_name, r.speed_limit, r.num_lanes
FROM Road r JOIN Zone z ON r.zone_id = z.zone_id
WHERE z.zone_name = 'Whitefield' AND r.speed_limit > 60;

-- Medium: Top 5 most congested junctions last 24 hours
SELECT j.junction_name, AVG(t.congestion_level) AS avg_congestion
FROM TrafficObservation t JOIN Junction j ON t.junction_id = j.junction_id
WHERE t.observation_time >= datetime('now', '-1 day')
GROUP BY j.junction_id, j.junction_name
ORDER BY avg_congestion DESC
LIMIT 5;

-- Complex: Incidents on roads where average speed < 30 kmph
SELECT i.incident_type, r.road_name, AVG(t.avg_speed_kmph) AS road_avg_speed
FROM Incident i
JOIN Road r ON i.road_id = r.road_id
JOIN TrafficObservation t ON t.road_id = r.road_id
GROUP BY i.incident_id, r.road_name
HAVING AVG(t.avg_speed_kmph) < 30;

-- Trigger: Auto-set congestion alert when vehicle count > 200
CREATE TRIGGER congestion_alert
AFTER INSERT ON TrafficObservation
WHEN NEW.vehicle_count > 200
BEGIN
    UPDATE Junction
    SET congestion_status = 'HIGH'
    WHERE junction_id = NEW.junction_id;
END;

-- View: Real-time dashboard view
CREATE VIEW TrafficDashboard AS
SELECT j.junction_name, j.zone_id,
       t.vehicle_count, t.congestion_level, t.observation_time,
       s.operational_status AS signal_status
FROM Junction j
LEFT JOIN TrafficObservation t ON j.junction_id = t.junction_id
LEFT JOIN TrafficSignal s ON j.junction_id = s.junction_id
WHERE t.observation_time = (
    SELECT MAX(t2.observation_time) FROM TrafficObservation t2
    WHERE t2.junction_id = j.junction_id
);
```

---

## 8. Technology Stack Recommendation

### Term 1
| Component | Recommendation | Why |
|---|---|---|
| Database | **SQLite** (required by lab) | Lab spec says so |
| DB Browser | **SQLiteBrowser** | Lab spec says so |
| Language | **Python** | Easy CSV import, Streamlit for UI |
| UI | **Streamlit** | 1 file, no frontend knowledge needed |
| ER Tool | **draw.io** (free) | Clean ER diagrams, shareable |
| Data | **Kaggle CSV** | Offline, clean, importable |

### Term 2 Extension
| Component | Recommendation |
|---|---|
| Database | **PostgreSQL + PostGIS** extension |
| Spatial queries | PostGIS ST_Distance, ST_Intersects |
| Time-series | TimescaleDB extension OR partitioned tables |
| Map viz | **Folium** (Python) or **Leaflet.js** |
| Image storage | File path in DB + BLOB for thumbnails |

---

## 9. Work-Integrated Activities Mapping

The handout requires 5 work-integrated activities (8 weeks):

| Activity | Topic | What You Submit |
|---|---|---|
| 1 | Conceptual Model | ER Diagram of traffic system |
| 2 | Logical DB Model | Tables in 3NF, functional dependencies, BCNF proof |
| 3 | Physical Design | Index design (B+ on timestamp), hash strategy |
| 4 | DB Administration | DBA challenges: concurrent updates, deadlock scenario |
| 5 | Security | Role-based access: Admin/Officer/Public, SQL GRANT/REVOKE |

---

## 10. Comparison: All 3 Options

| Criteria | Urban Traffic (Pick 2) | Hospital (Pick 1) | E-Commerce (Pick 3) |
|---|---|---|---|
| Data availability | High (OSM, Kaggle) | Low (health data is private) | Medium (synthetic ok) |
| Syllabus fit | Excellent | Excellent | Good |
| Term 2 complexity | High (GIS/spatial) | Medium (DICOM images) | Low (product images) |
| Real-world relevance | Very High | Very High | High |
| ITA/MTech portfolio value | High (infra/smart city angle) | High (health-tech angle) | Medium |
| 2-person feasibility | Excellent | Excellent | Good |
| Risk of data fabrication needed | Low | High | Low |

### Why NOT Hospital (Option 1):
- Patient data is sensitive — public datasets are heavily anonymized or unavailable in India
- You'll end up fabricating all data, which weakens authenticity
- DICOM image handling in Term 2 is complex without domain knowledge

### Why NOT E-Commerce (Option 3):
- Conceptually simpler — fewer interesting DBMS challenges
- Most students pick this; less differentiated at viva
- Term 2 extension is relatively shallow compared to GIS/spatial

---

## 11. Risk Register

| Risk | Probability | Mitigation |
|---|---|---|
| Real-time data too complex | Medium | Use batch Kaggle data, simulate real-time with Python |
| Scope creep (too many entities) | High | Hard cap: max 10 entities in Term 1 |
| Term 2 PostGIS learning curve | Medium | Start PostGIS tutorial in Week 6 of Term 1 |
| Viva questions on spatial indexing | Medium | Practice R-Tree vs B+ Tree explanation |
| SQLite limitations for Term 2 | High | Migrate to PostgreSQL at Term 2 start — plan for it |

---

## 12. SRS Requirements Checklist (Term 1)

### Functional Requirements
- [ ] FR1: System shall store road network data (roads, junctions, zones)
- [ ] FR2: System shall record vehicle registrations and driver details
- [ ] FR3: System shall log traffic observations at junctions with timestamps
- [ ] FR4: System shall manage traffic incidents (accidents, breakdowns, roadblocks)
- [ ] FR5: System shall manage traffic signal status and timing
- [ ] FR6: System shall generate congestion reports by zone/time
- [ ] FR7: System shall support incident search by road, junction, type, and date range
- [ ] FR8: System shall maintain sensor installation and status records
- [ ] FR9: System shall support role-based access (Admin, Traffic Officer, Public Read)
- [ ] FR10: System shall enforce referential integrity across all tables

### Non-Functional Requirements
- [ ] NFR1: Query response for any single-table lookup < 2 seconds
- [ ] NFR2: System shall handle 10,000+ traffic observation records
- [ ] NFR3: All transactions shall satisfy ACID properties
- [ ] NFR4: Database shall recover to consistent state after simulated crash
- [ ] NFR5: All tables shall be in BCNF (with documented exceptions if any)
- [ ] NFR6: Index strategy shall be documented and justified

### Deliverables
- [ ] SRS Document (problem statement, scope, requirements, users)
- [ ] ER/EER Diagram (draw.io or similar)
- [ ] Relational Schema (all tables, PKs, FKs, constraints)
- [ ] Normalization Report (FDs, 1NF → BCNF steps for each table)
- [ ] SQL Script (CREATE, INSERT, SELECT, UPDATE, DELETE, Views, Triggers)
- [ ] Index Design Document (which indexes, why, B+ tree sketches)
- [ ] Application Prototype (Python/Streamlit demo)
- [ ] Transaction Demonstration (ACID scenario, lock protocol)
- [ ] Security Design (user roles, GRANT/REVOKE statements)
- [ ] Recovery Demo (WAL log, checkpoint scenario)

---

## 13. 8-Week Execution Timeline (2 People)

| Week | Person A | Person B | Shared |
|---|---|---|---|
| 1 | SRS draft, scope definition | Data sourcing (Kaggle) | Problem statement + users |
| 2 | ER diagram v1 | Data cleaning scripts | ER review meeting |
| 3 | ER → Relational mapping | SQLite schema creation | Schema review |
| 4 | Normalization (FDs, BCNF) | Data import + basic SELECT | Normalization verification |
| 5 | Indexing design + B+ Tree | Complex SQL queries (joins, aggregates) | Query testing |
| 6 | Transaction + concurrency demo | Application prototype (Streamlit) | Integration |
| 7 | Security (roles, GRANT/REVOKE) | Recovery scenario demo | Full integration test |
| 8 | Final SRS polish | Prototype polish | Viva preparation |

---

## 14. Viva Preparation: Expected Hard Questions

1. Why did you choose this index structure over a hash index for junction lookups?
2. Demonstrate a situation where your schema would have a lost update without 2PL.
3. Walk me through the BCNF decomposition of TrafficObservation.
4. How does your recovery mechanism handle a crash mid-transaction?
5. What changes to your schema would you need for Term 2 spatial data?
6. Why is a B+ tree preferred over a B tree for your timestamp index?
7. Show me a query that benefits from your index vs one that does a full table scan.

---

*Generated: September 2026 | BITS Pilani WILP | SESAP ZC337*
