# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## Urban Road & Real-Time Traffic Information and Management Database System

**Document Version:** 2.0  
**Prepared by:** Nimisha Gupta  
**Course:** SESAP ZC337 — Database Systems and Applications  
**Institute:** BITS Pilani, Work Integrated Learning Programmes (WILP)  
**Date:** October 2026  
**Standard:** IEEE 830-1998 / ISO/IEC/IEEE 29148:2018  
**Lab Session 2 Deadline:** 17 October 2026

---

## Table of Contents

1. Introduction
2. Overall Description
3. Specific Requirements
4. Database Design
5. Frontend Requirements and Specifications
6. Backend — API, Connectivity, and Application
7. System Features (DBMS Concepts)
8. External Interface Requirements
9. Validation and Verification
10. Work-Integrated Activities Mapping
11. Appendix

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the complete requirements for the **Urban Road & Real-Time Traffic Information and Management Database System**, a three-tier web application backed by a fully normalized relational database. The system manages Bengaluru's road network, real-time traffic observations, incident reporting, traffic signal management, and vehicle records. It serves traffic police officers, city planners, emergency services, and the public through role-differentiated access.

This document is structured per **IEEE 830-1998** and **ISO/IEC/IEEE 29148:2018** and serves as the authoritative reference for developers, evaluators, and the lab examiner.

### 1.2 Scope

**System Name:** Urban Traffic Management System (UTMS)  
**City in Scope:** Bengaluru, Karnataka, India  
**Term 1 Scope:** Fully normalized relational database, REST API backend, interactive HTML/JS frontend with live map, CI/CD pipeline with Docker.

The system enables:
- Storage and retrieval of road and junction network data
- Real-time (simulated) traffic observation logging
- Incident registration, tracking, and resolution
- Traffic signal status management
- Vehicle and driver registration
- Congestion analytics by zone, time window, and road segment
- Interactive Leaflet.js map showing live congestion and incidents
- Role-based access control (Admin / Traffic Officer / Public)

**Out of scope (Term 1):** Live sensor streaming, GIS spatial queries via PostGIS, image/video storage, mobile application.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Meaning |
|------|---------|
| DBMS | Database Management System |
| SRS | Software Requirements Specification |
| DDL | Data Definition Language |
| DML | Data Manipulation Language |
| PK | Primary Key |
| FK | Foreign Key |
| SQL | Structured Query Language |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| ACID | Atomicity, Consistency, Isolation, Durability |
| 2PL | Two-Phase Locking |
| BCNF | Boyce-Codd Normal Form |
| ER | Entity-Relationship |
| EER | Enhanced Entity-Relationship |
| UTMS | Urban Traffic Management System |
| CI/CD | Continuous Integration / Continuous Deployment |
| WAL | Write-Ahead Log |
| RBAC | Role-Based Access Control |
| WIA | Work-Integrated Activity |

### 1.4 References

- IEEE 830-1998: IEEE Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2018: Systems and Software Engineering — Life Cycle Processes — Requirements Engineering
- Elmasri & Navathe, *Fundamentals of Database Systems*, 7th Edition, Pearson
- SQLite Documentation: https://www.sqlite.org/docs.html
- BITS Pilani SESAP ZC337 Lab Assignment Handout, Version 1.0, September 2026
- Project ER Diagram Specification: `docs/ER_Diagram_Specification.md`
- Project Schema: `sql/schema.sql`
- Seed Data: `sql/seed_data.sql`
- Triggers and Views: `sql/triggers.sql`

---

## 2. Overall Description

### 2.1 Product Perspective

The Urban Traffic Management System is a three-tier web application:

```
┌─────────────────────────────────────────────┐
│  Presentation Tier (Frontend)               │
│  HTML / CSS / Vanilla JavaScript            │
│  5 screens: Dashboard (Leaflet map), Traffic│
│  Observations, Incident Management,         │
│  Add Observation, Roads & Junctions         │
└────────────────────┬────────────────────────┘
                     │ HTTP REST (JSON)
                     │ fetch() with X-User-Role header
┌────────────────────▼────────────────────────┐
│  Application Tier (Backend)                 │
│  Python Flask REST API                      │
│  14 endpoints, parameterized SQL,           │
│  ACID transactions, RBAC middleware         │
└────────────────────┬────────────────────────┘
                     │ sqlite3 stdlib connector
                     │ PRAGMA foreign_keys=ON
                     │ PRAGMA journal_mode=WAL
┌────────────────────▼────────────────────────┐
│  Data Tier (Database)                       │
│  SQLite 3.x (data/traffic.db)               │
│  10 tables + 8 ISA subtype tables,          │
│  3 views, 4 triggers, 9 indexes,            │
│  1 audit log table                          │
└─────────────────────────────────────────────┘
```

This architecture implements the **Three-Schema Architecture** (ANSI/SPARC):

| Schema Level | Implementation |
|---|---|
| **External Schema** | SQL VIEWs: `TrafficDashboard`, `ZoneSummary`, `IncidentReport` — each user role sees a tailored view of the data |
| **Conceptual Schema** | 10 normalized tables in BCNF: Zone, Road, Junction, Road_Junction, Traffic_Signal, Driver, Vehicle, Incident, Traffic_Observation, Sensor |
| **Internal Schema** | Physical storage via SQLite: 9 B+ tree / hash-equivalent indexes, WAL journal mode, page-based storage |

### 2.2 Product Functions

| Function | Description |
|----------|-------------|
| Road Network Management | Store and query roads, junctions, zones, and their relationships |
| Traffic Observation Logging | Record vehicle count, average speed, congestion level at junctions |
| Incident Management | Log, update, resolve, and delete traffic incidents |
| Signal Management | Track traffic signal status, timing, and operational health |
| Vehicle & Driver Registry | Maintain vehicle registrations linked to driver/owner details |
| Congestion Analytics | Aggregate reports by zone, time range, road segment; peak-hour analysis |
| Live Congestion Map | Leaflet.js map showing junction congestion (colour-coded) and open incidents |
| Role-Based Access | Enforce Admin / Traffic Officer / Public access tiers |
| Data Integrity | PK/FK constraints, triggers, CHECK constraints, NOT NULL rules |
| Audit Logging | Automatic audit trail of all incident changes via AFTER trigger |
| ACID Transactions | Explicit BEGIN/COMMIT/ROLLBACK for all multi-step operations |
| WAL Recovery | Write-Ahead Log mode ensuring durability and concurrent read access |

### 2.3 User Characteristics

| User Role | Description | Access Level | Technical Level |
|-----------|-------------|--------------|-----------------|
| System Admin | Manages schema, users, roles, backups; can delete records | Full DDL + DML | High |
| Traffic Officer / Control Room | Logs incidents and observations; can resolve incidents | INSERT + UPDATE + SELECT | Medium |
| City Planner / Municipal Authority | Generates reports, analyses congestion | SELECT only | Low–Medium |
| Emergency Services | Queries incidents and fastest-route data | SELECT only | Low |
| Commuter (Public) | Views congestion and signal status | SELECT (public views only) | Low |

### 2.4 Constraints

- Database MUST be implemented in **SQLite 3.x** (per lab specification)
- All tables MUST be in **BCNF** (with documented justification)
- All referential integrity MUST be enforced via **FOREIGN KEY constraints** with `PRAGMA foreign_keys = ON`
- Backend MUST use **parameterized SQL** — no string concatenation in queries
- Frontend MUST be simple HTML/CSS/JS — no React, no server-side rendering
- CI pipeline MUST trigger on every `git push`
- System MUST demonstrate **ACID properties** through explicit transaction scenarios
- Role enforcement via `X-User-Role` HTTP header (simulating authentication layer)

### 2.5 Assumptions and Dependencies

- Data scope is limited to Bengaluru for Term 1 (5 zones, 15 junctions, 20 roads seeded)
- Real-time sensor data is simulated via batch INSERT from `sql/seed_data.sql`
- SQLite 3.x with `PRAGMA foreign_keys = ON` and `PRAGMA journal_mode = WAL`
- Python 3.10+ with Flask 3.0+
- GitHub repository used for CI/CD via GitHub Actions
- Docker used for containerized deployment
- Leaflet.js loaded from CDN (unpkg.com) — requires internet for map tiles; offline-capable for all other features

---

## 3. Specific Requirements

### 3.1 Functional Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| FR1 | Store and manage zone data (zone_id, zone_name, city, area, zone_type) | ✓ Implemented |
| FR2 | Store road data including road type, lane count, speed limit, surface type, and zone association | ✓ Implemented |
| FR3 | Store junction data including GPS coordinates, junction type, and signal control status | ✓ Implemented |
| FR4 | Maintain M:N relationships between roads and junctions via bridge table Road_Junction | ✓ Implemented |
| FR5 | Store traffic signal configurations including timing and operational status | ✓ Implemented |
| FR6 | Register drivers/owners with license details and contact information | ✓ Implemented |
| FR7 | Register vehicles with license plate (unique), type, make, model, and owner linkage | ✓ Implemented |
| FR8 | Support EER specialisation of vehicles into Car, Truck, Motorcycle, Bus | ✓ Implemented |
| FR9 | Log traffic observations at junctions with timestamp, vehicle count, speed, congestion, weather | ✓ Implemented |
| FR10 | Log traffic incidents with type, severity, description, timestamps, and road/junction/vehicle links | ✓ Implemented |
| FR11 | Support EER specialisation of incidents into Accident, Breakdown, Roadblock, Flooding | ✓ Implemented |
| FR12 | Maintain sensor installation records and health status at junctions | ✓ Implemented |
| FR13 | Auto-flag junctions as HIGH congestion via trigger when vehicle_count > 200 | ✓ Implemented |
| FR14 | Auto-audit all incident modifications via AFTER trigger into Audit_Log table | ✓ Implemented |
| FR15 | Provide real-time dashboard view aggregating latest observations per junction | ✓ Implemented |
| FR16 | Support congestion reporting by zone and time window | ✓ Implemented |
| FR17 | Support incident search by road, junction, type, severity, and date range | ✓ Implemented |
| FR18 | Provide interactive map showing junction congestion (colour-coded) and open incidents | ✓ Implemented |
| FR19 | Enforce role-based access (Admin, TrafficOfficer, Public) via application-layer RBAC | ✓ Implemented |
| FR20 | Support full CRUD operations on traffic observations and incidents via REST API | ✓ Implemented |
| FR21 | Return all API responses in JSON format with appropriate HTTP status codes | ✓ Implemented |
| FR22 | Validate all API inputs before executing SQL; reject malformed requests with 400 | ✓ Implemented |
| FR23 | Demonstrate ACID transactions (observation insert + junction update in one transaction) | ✓ Implemented |
| FR24 | Provide recovery demonstration via SQLite WAL mode and checkpoint | ✓ Implemented |
| FR25 | Provide peak-hour analytics endpoint grouping observations by hour of day | ✓ Implemented |
| FR26 | Provide audit log endpoint (Admin only) showing all data modification history | ✓ Implemented |

### 3.2 Non-Functional Requirements

| ID | Category | Requirement | Status |
|----|----------|-------------|--------|
| NFR1 | Performance | Single-table SELECT queries shall complete in < 2 seconds for up to 10,000 records | ✓ |
| NFR2 | Performance | Multi-table JOIN queries (≤ 5 tables) shall complete in < 3 seconds for ≤ 1,000 records | ✓ |
| NFR3 | Security | Only users with Admin role may execute DELETE on incidents and view audit log | ✓ |
| NFR4 | Security | Traffic Officer may INSERT/UPDATE observations and incidents; cannot DELETE records | ✓ |
| NFR5 | Security | Public role may only execute GET on public read endpoints | ✓ |
| NFR6 | Reliability | Database shall enforce NOT NULL and CHECK constraints to prevent corrupt records | ✓ |
| NFR7 | Reliability | All foreign key constraints shall be active (PRAGMA foreign_keys = ON) | ✓ |
| NFR8 | Scalability | Schema shall support growth to 100,000 traffic observations and 50,000 vehicles | ✓ |
| NFR9 | Maintainability | All tables shall be in BCNF; documented in Section 4.3 | ✓ |
| NFR10 | Recoverability | Database shall recover to consistent state after simulated crash using WAL + checkpoint | ✓ |
| NFR11 | Indexing | Composite B+ tree index on (junction_id, observation_time) for fast time-series queries | ✓ |
| NFR12 | Indexing | UNIQUE index on license_plate for O(log n) vehicle lookups | ✓ |
| NFR13 | Portability | Application shall run in Docker container on any Linux/macOS host | ✓ |
| NFR14 | Traceability | All SQL queries shall use parameterized statements (no raw string interpolation) | ✓ |
| NFR15 | Testability | Automated pytest suite with ≥ 20 test cases covering CRUD, RBAC, validation | ✓ 27 tests |

### 3.3 Domain Requirements

- Traffic observation data complies with BBMP (Bruhat Bengaluru Mahanagara Palike) road network classification
- Incident severity must be one of: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Congestion level must be one of: `LOW`, `MODERATE`, `HIGH`, `SEVERE`
- Vehicle type must be one of: `Car`, `Truck`, `Motorcycle`, `Bus`, `Auto`, `Other`
- Speed limit values must be between 10 and 120 km/h
- Junction coordinates must be valid Bengaluru GPS coordinates (lat: 12.7–13.2, lon: 77.4–77.8)
- All timestamps stored in ISO 8601 format (`YYYY-MM-DD HH:MM:SS`)

---

## 4. Database Design

### 4.1 Three-Schema Architecture Detail

#### External Schema — SQL Views

Three views provide role-appropriate external schemas:

**TrafficDashboard** (Public + Officer): Latest observation per junction joined with zone and signal data:
```sql
CREATE VIEW TrafficDashboard AS
SELECT j.junction_id, j.junction_name, z.zone_name, z.zone_type,
       t.observation_time, t.vehicle_count, t.avg_speed_kmph,
       t.congestion_level, t.weather_condition,
       s.operational_status AS signal_status
FROM Junction j
LEFT JOIN Zone z ON j.zone_id = z.zone_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
    AND t.observation_time = (
        SELECT MAX(t2.observation_time) FROM Traffic_Observation t2
        WHERE t2.junction_id = j.junction_id
    )
LEFT JOIN Traffic_Signal s ON j.junction_id = s.junction_id;
```

**ZoneSummary** (Planner): Aggregated statistics per zone over the last 24 hours.

**IncidentReport** (Officer + Admin): Open incidents joined with road and junction names.

#### Conceptual Schema — 10 Normalized Tables

See Section 4.5 (Data Dictionary) for full column definitions.

#### Internal Schema — Physical Storage

- **File organization:** SQLite heap file (sequential insertion, rowid clustering)
- **Journaling:** WAL (Write-Ahead Log) — `PRAGMA journal_mode = WAL`
- **Page size:** 4096 bytes (SQLite default)
- **Indexes:** 9 named indexes (B+ tree equivalent in SQLite)

### 4.2 ER / EER Conceptual Model

The conceptual model uses **EER (Enhanced Entity-Relationship)** notation:

- **10 strong entity types** (no weak entities)
- **2 EER specialisation hierarchies** (ISA)
- **1 M:N relationship** resolved via associative/bridge entity
- **11 binary relationships** total

> **Complete ER Diagram Specification** (Chen notation, entity/attribute lists, relationship table, ISA hierarchies, drawing instructions, AI image prompt, draw.io guide):  
> See `docs/ER_Diagram_Specification.md`

#### Entity Summary

| # | Entity | Primary Key | Description |
|---|--------|-------------|-------------|
| 1 | ZONE | zone_id | Administrative city zone (Whitefield, Koramangala, etc.) |
| 2 | ROAD | road_id | Road segment with type, lanes, speed limit |
| 3 | JUNCTION | junction_id | Intersection/junction with GPS coordinates |
| 4 | ROAD_JUNCTION | (road_id, junction_id) | Bridge table for M:N Road–Junction relationship |
| 5 | TRAFFIC_SIGNAL | signal_id | Traffic signal at a junction with timing configuration |
| 6 | DRIVER | driver_id | Vehicle owner/driver with license details |
| 7 | VEHICLE | vehicle_id | Registered vehicle linked to a driver |
| 8 | INCIDENT | incident_id | Traffic event at road/junction, optionally involving a vehicle |
| 9 | TRAFFIC_OBSERVATION | obs_id | Timestamped traffic measurement at a junction |
| 10 | SENSOR | sensor_id | Physical sensing device installed at a junction |

#### Relationship Summary

| # | Relationship | Entities | Cardinality | Participation |
|---|---|---|---|---|
| R1 | BELONGS_TO | ROAD → ZONE | M:1 | Road: total; Zone: partial |
| R2 | LOCATED_IN | JUNCTION → ZONE | M:1 | Junction: total; Zone: partial |
| R3 | CONNECTS | ROAD ↔ JUNCTION | M:N | Resolved via ROAD_JUNCTION bridge |
| R4 | HAS_SIGNAL | JUNCTION → TRAFFIC_SIGNAL | 1:M | Signal: total (must belong to junction) |
| R5 | OWNS | DRIVER → VEHICLE | 1:M | Vehicle: partial (owner_id nullable) |
| R6 | OBSERVED_AT | TRAFFIC_OBSERVATION → JUNCTION | M:1 | Observation: total |
| R7 | RECORDED_ON | TRAFFIC_OBSERVATION → ROAD | M:1 | Observation: total |
| R8 | OCCURS_ON | INCIDENT → ROAD | M:1 | Incident: partial (nullable FK) |
| R9 | OCCURS_AT | INCIDENT → JUNCTION | M:1 | Incident: partial (nullable FK) |
| R10 | INVOLVES | INCIDENT → VEHICLE | M:1 | Incident: partial (nullable FK) |
| R11 | INSTALLED_AT | SENSOR → JUNCTION | M:1 | Sensor: total |

#### EER Specialisations (ISA Hierarchies)

```
VEHICLE  [Total Participation, Disjoint — double line, "d" inside triangle]
              |
         [ISA / d]
       /    |    |    \
     CAR  TRUCK MOTO  BUS
     (num_doors,  (max_load_  (engine_  (seating_
      fuel_type)   tonnes)     cc)       capacity)

INCIDENT  [Partial Participation, Disjoint — single line, "d" inside triangle]
              |
         [ISA / d]
       /     |     |      \
  ACCIDENT BREAKDOWN ROADBLOCK FLOODING
  (injuries_ (breakdown_ (authority_ (water_level_
   count,      cause)      name)       cm)
   fatalities)
```

**Total participation** (VEHICLE): every vehicle row must have exactly one subtype row.  
**Partial participation** (INCIDENT): some incidents may not belong to any subtype (generic observations).  
**Disjoint**: a vehicle cannot be both a Car and a Truck; an incident cannot be both Accident and Flooding.

### 4.3 ER-to-Relational Mapping (All 7 Rules Applied)

**Rule 1 — Regular (Strong) Entity Types:**  
Each strong entity becomes a relation. PK preserved.

```
Zone(zone_id PK, zone_name, city, area_sqkm, zone_type)
Road(road_id PK, road_name, road_type, length_km, num_lanes, speed_limit,
     surface_type, direction_type, zone_id FK→Zone)
Junction(junction_id PK, junction_name, junction_type, latitude, longitude,
         signal_controlled, congestion_status, zone_id FK→Zone)
Traffic_Signal(signal_id PK, signal_type, installed_date, operational_status,
               green_duration_sec, junction_id FK→Junction)
Driver(driver_id PK, name, license_no UNIQUE, dob, contact, address)
Vehicle(vehicle_id PK, license_plate UNIQUE, vehicle_type, make, model, year,
        registered_state, owner_id FK→Driver)
Sensor(sensor_id PK, sensor_type, installation_date, status,
       last_reading_time, junction_id FK→Junction)
```

**Rule 2 — Weak Entity Types:** Not applicable — all entities have surrogate PKs.

**Rule 3 — Binary 1:1 Relationships:** Not applicable.

**Rule 4 — Binary 1:N Relationships:**  
FK placed on the N-side:
- `Road.zone_id → Zone.zone_id`
- `Junction.zone_id → Zone.zone_id`
- `Traffic_Signal.junction_id → Junction.junction_id`
- `Vehicle.owner_id → Driver.driver_id`
- `Sensor.junction_id → Junction.junction_id`
- `Traffic_Observation.junction_id → Junction.junction_id`
- `Traffic_Observation.road_id → Road.road_id`
- `Incident.road_id → Road.road_id` (nullable — partial participation)
- `Incident.junction_id → Junction.junction_id` (nullable)
- `Incident.vehicle_id → Vehicle.vehicle_id` (nullable)

**Rule 5 — Binary M:N Relationships:**  
New bridge relation with composite PK:
```
Road_Junction(road_id PK+FK→Road, junction_id PK+FK→Junction, position_type)
```

**Rule 6 — Multivalued Attributes:** Not applicable.

**Rule 7 — N-ary Relationships:** Not applicable.

**ISA Mapping (one table per subtype, shared PK):**
```
Car(vehicle_id PK+FK→Vehicle, num_doors, fuel_type)
Truck(vehicle_id PK+FK→Vehicle, max_load_tonnes)
Motorcycle(vehicle_id PK+FK→Vehicle, engine_cc)
Bus(vehicle_id PK+FK→Vehicle, seating_capacity)

Accident(incident_id PK+FK→Incident, injuries_count, fatalities)
Breakdown(incident_id PK+FK→Incident, breakdown_cause)
Roadblock(incident_id PK+FK→Incident, authority_name)
Flooding(incident_id PK+FK→Incident, water_level_cm)
```

**Audit Table (additional system table):**
```
Audit_Log(log_id PK, table_name, record_id, action, changed_by, changed_at, old_values, new_values)
```

### 4.4 Normalization Analysis

#### TRAFFIC_OBSERVATION — Full BCNF Walkthrough

**Starting unnormalized record:**
```
ObsRecord = {obs_id, junction_id, junction_name, zone_id, road_id, road_name,
             observation_time, vehicle_count, avg_speed_kmph, congestion_level,
             weather_condition, data_source}
```

**Step 1 — First Normal Form (1NF):**
- Condition: all attributes atomic, no repeating groups, no set-valued attributes
- Check: every cell holds a single atomic value; no multi-valued fields
- Result: ✓ 1NF satisfied

**Step 2 — Second Normal Form (2NF):**
- PK is `obs_id` (single-attribute) — no composite PK exists
- No partial dependency is possible with a single-attribute PK
- Result: ✓ 2NF automatically satisfied

**Step 3 — Third Normal Form (3NF):**
- Functional Dependencies identified:
  - `obs_id → {junction_id, road_id, observation_time, vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source}` ✓ (non-trivial, LHS is PK)
  - `junction_id → {junction_name, zone_id}` — transitive dependency detected!
    - `obs_id → junction_id → junction_name` (transitive chain)
  - `road_id → road_name` — transitive dependency detected!
- Resolution: Remove `junction_name`, `zone_id`, `road_name` from Traffic_Observation; retain FKs. These attributes live in Junction and Road tables.
- Result: ✓ 3NF achieved after decomposition

**Step 4 — Boyce-Codd Normal Form (BCNF):**
- Condition: for every non-trivial FD `X → Y`, X must be a superkey
- After 3NF decomposition, `obs_id` is the only determinant for all non-key attributes in Traffic_Observation
- No non-trivial FD where LHS is not a superkey remains
- Result: ✓ BCNF verified

**Lossless Join Property:**  
Decomposition of R(obs_id, junction_id, junction_name) into:
- R1(obs_id, junction_id) and R2(junction_id, junction_name)
- R1 ∩ R2 = {junction_id}; `junction_id → junction_name` holds in R2
- Therefore: lossless join ✓

**Dependency Preservation:**  
All FDs from the original relation are preserved across the decomposed tables. No FD is lost.

#### BCNF Verification — All Tables

| Table | 1NF | 2NF | 3NF | BCNF | Justification |
|-------|-----|-----|-----|------|---------------|
| Zone | ✓ | ✓ | ✓ | ✓ | Single PK, no transitive dependencies |
| Road | ✓ | ✓ | ✓ | ✓ | zone_id is FK (not transitive from road_id) |
| Junction | ✓ | ✓ | ✓ | ✓ | zone_id is FK, lat/lon functionally determined by junction_id |
| Road_Junction | ✓ | ✓ | ✓ | ✓ | Composite PK; position_type determined by full PK |
| Traffic_Signal | ✓ | ✓ | ✓ | ✓ | Single PK signal_id; junction_id is FK |
| Driver | ✓ | ✓ | ✓ | ✓ | license_no is candidate key (UNIQUE), not a transitive dep. |
| Vehicle | ✓ | ✓ | ✓ | ✓ | license_plate is candidate key; owner_id is FK |
| Incident | ✓ | ✓ | ✓ | ✓ | All non-key attrs depend solely on incident_id; nullable FKs are design choice |
| Traffic_Observation | ✓ | ✓ | ✓ | ✓ | Full walkthrough above |
| Sensor | ✓ | ✓ | ✓ | ✓ | junction_id is FK; all attrs depend on sensor_id |

**Conclusion:** No update, insertion, or deletion anomalies exist in the current schema.

### 4.5 Physical Design — Indexing Strategy

#### B+ Tree Indexes (Range Queries and Join Optimization)

| Index Name | Table | Column(s) | Query Pattern | Justification |
|-----------|-------|-----------|---------------|---------------|
| `idx_obs_junction_time` | Traffic_Observation | (junction_id, observation_time) | Dashboard: latest obs per junction | Composite covering index; left-prefix used for junction filter, right-prefix for time range/MAX |
| `idx_obs_road` | Traffic_Observation | road_id | Filter observations by road segment | Avoids full scan on road-level queries |
| `idx_incident_road` | Incident | road_id | Incident search by road | JOIN optimization |
| `idx_incident_junction` | Incident | junction_id | Incident search by junction | JOIN optimization |
| `idx_incident_datetime` | Incident | reported_datetime | Date-range incident queries | Range scan using B+ tree leaf-link list |
| `idx_road_zone` | Road | zone_id | Zone-filtered road listing | JOIN on zone_id |
| `idx_junction_zone` | Junction | zone_id | Zone-filtered junction listing | JOIN on zone_id |

#### Hash-Equivalent Indexes (Exact Equality Lookups)

| Index Name | Table | Column | Mechanism | Justification |
|-----------|-------|--------|-----------|---------------|
| `idx_vehicle_plate` | Vehicle | license_plate | UNIQUE constraint → implicit index | Vehicle lookup by plate: equality only, no range, O(log n) lookup |
| `idx_driver_license` | Driver | license_no | UNIQUE constraint → implicit index | License number lookup for driver verification |

#### B+ Tree vs Hash — Design Rationale

**B+ Tree chosen for time-series and range queries:**
- Supports `WHERE observation_time BETWEEN t1 AND t2` efficiently via linked leaf list
- Supports `ORDER BY observation_time DESC` without extra sort
- Internal nodes store separator keys only; all data in leaf nodes (dense index)
- Sequential scan traverses leaf nodes as a linked list — no full tree traversal
- Preferred over B-tree because B+ tree leaf nodes are linked, enabling range scans in O(1) extra cost

**Hash-equivalent (UNIQUE index) chosen for plate/license lookups:**
- Only equality predicates ever issued: `WHERE license_plate = 'KA-01-AB-1234'`
- No range queries, no ORDER BY on these columns
- SQLite UNIQUE constraint creates an implicit index with O(log n) lookup
- Conceptually equivalent to static external hashing: bucket = hash(plate) mod M

### 4.6 Data Dictionary

#### Table: Zone

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| zone_id | INTEGER | PK, NOT NULL | Surrogate zone identifier |
| zone_name | TEXT | NOT NULL, UNIQUE | Name (e.g., "Whitefield", "Koramangala") |
| city | TEXT | NOT NULL, DEFAULT 'Bengaluru' | City name |
| area_sqkm | REAL | CHECK (area_sqkm > 0) | Zone area in square kilometres |
| zone_type | TEXT | CHECK IN ('Residential','Commercial','Industrial','Mixed','Government') | Zone classification |

#### Table: Road

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| road_id | INTEGER | PK, NOT NULL | Surrogate road identifier |
| road_name | TEXT | NOT NULL | Full road name |
| road_type | TEXT | CHECK IN ('National Highway','State Highway','City Road','Lane','Ring Road') | Road classification |
| length_km | REAL | CHECK (length_km > 0) | Road segment length in km |
| num_lanes | INTEGER | CHECK (num_lanes > 0) | Number of lanes |
| speed_limit | INTEGER | CHECK BETWEEN 10 AND 120 | Speed limit in km/h |
| surface_type | TEXT | — | Asphalt / Concrete / Gravel |
| direction_type | TEXT | — | One-way / Two-way / Divided |
| zone_id | INTEGER | FK → Zone.zone_id, NOT NULL | Zone this road belongs to |

#### Table: Junction

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| junction_id | INTEGER | PK, NOT NULL | Surrogate junction identifier |
| junction_name | TEXT | NOT NULL | Name (e.g., "Silk Board Junction") |
| junction_type | TEXT | CHECK IN ('Signalised','Unsignalised','Roundabout','Flyover','Interchange') | Junction classification |
| latitude | REAL | CHECK BETWEEN 12.7 AND 13.2 | Bengaluru latitude range |
| longitude | REAL | CHECK BETWEEN 77.4 AND 77.8 | Bengaluru longitude range |
| signal_controlled | INTEGER | DEFAULT 0 | 0 = No, 1 = Yes |
| congestion_status | TEXT | DEFAULT 'NORMAL' | NORMAL / HIGH — auto-updated by trigger |
| zone_id | INTEGER | FK → Zone.zone_id, NOT NULL | Zone this junction belongs to |

#### Table: Road_Junction

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| road_id | INTEGER | PK (composite), FK → Road | Road in the pairing |
| junction_id | INTEGER | PK (composite), FK → Junction | Junction in the pairing |
| position_type | TEXT | — | Start / End / Intermediate |

#### Table: Traffic_Signal

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| signal_id | INTEGER | PK, NOT NULL | Surrogate signal identifier |
| junction_id | INTEGER | FK → Junction, NOT NULL | Junction where signal is installed |
| signal_type | TEXT | — | Standard / Adaptive / Pedestrian |
| installed_date | DATE | — | Date first installed |
| operational_status | TEXT | CHECK IN ('Active','Inactive','Faulty','Under Maintenance') | Current status |
| green_duration_sec | INTEGER | CHECK (> 0) | Green phase duration in seconds |

#### Table: Driver

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| driver_id | INTEGER | PK, NOT NULL | Surrogate driver identifier |
| name | TEXT | NOT NULL | Full legal name |
| license_no | TEXT | UNIQUE, NOT NULL | Driving license number (candidate key) |
| dob | DATE | — | Date of birth |
| contact | TEXT | — | Phone number |
| address | TEXT | — | Residential address |

#### Table: Vehicle

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| vehicle_id | INTEGER | PK, NOT NULL | Surrogate vehicle identifier |
| license_plate | TEXT | UNIQUE, NOT NULL | Registration number, e.g., KA-01-AB-1234 |
| vehicle_type | TEXT | CHECK IN ('Car','Truck','Motorcycle','Bus','Auto','Other') | Vehicle classification |
| make | TEXT | — | Manufacturer (Maruti, Tata, etc.) |
| model | TEXT | — | Model name |
| year | INTEGER | CHECK BETWEEN 1990 AND 2030 | Manufacturing year |
| registered_state | TEXT | — | State of registration |
| owner_id | INTEGER | FK → Driver.driver_id | Owner/driver reference |

#### Table: Incident

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| incident_id | INTEGER | PK, NOT NULL | Surrogate incident identifier |
| incident_type | TEXT | NOT NULL, CHECK IN ('Accident','Breakdown','Roadblock','Flooding') | Incident classification |
| severity | TEXT | CHECK IN ('LOW','MEDIUM','HIGH','CRITICAL') | Severity rating |
| description | TEXT | — | Free-text description |
| reported_datetime | DATETIME | NOT NULL, DEFAULT datetime('now') | When incident was reported |
| resolved_datetime | DATETIME | — | When resolved; NULL = open incident |
| road_id | INTEGER | FK → Road (nullable) | Road where incident occurred |
| junction_id | INTEGER | FK → Junction (nullable) | Junction at incident site |
| vehicle_id | INTEGER | FK → Vehicle (nullable) | Vehicle involved |
| reported_by | TEXT | — | Name or role of reporting party |

#### Table: Traffic_Observation

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| obs_id | INTEGER | PK, NOT NULL | Surrogate observation identifier |
| junction_id | INTEGER | FK → Junction, NOT NULL | Junction being observed |
| road_id | INTEGER | FK → Road, NOT NULL | Road segment being observed |
| observation_time | DATETIME | NOT NULL, DEFAULT datetime('now') | ISO 8601 timestamp |
| vehicle_count | INTEGER | CHECK (>= 0) | Total vehicles counted in period |
| avg_speed_kmph | REAL | CHECK (>= 0) | Average speed in km/h |
| congestion_level | TEXT | CHECK IN ('LOW','MODERATE','HIGH','SEVERE') | Congestion classification |
| weather_condition | TEXT | — | Clear / Rainy / Foggy / Cloudy |
| data_source | TEXT | — | Sensor / Manual / Camera |

#### Table: Sensor

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| sensor_id | INTEGER | PK, NOT NULL | Surrogate sensor identifier |
| sensor_type | TEXT | — | Inductive Loop / Camera / Radar / CCTV |
| junction_id | INTEGER | FK → Junction, NOT NULL | Junction where installed |
| installation_date | DATE | — | Date installed |
| status | TEXT | CHECK IN ('Active','Inactive','Faulty') | Current operational status |
| last_reading_time | DATETIME | — | Timestamp of most recent data received |

#### Table: Audit_Log

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| log_id | INTEGER | PK, AUTOINCREMENT | Audit record identifier |
| table_name | TEXT | NOT NULL | Table that was modified |
| record_id | INTEGER | NOT NULL | PK of the modified record |
| action | TEXT | NOT NULL | INSERT / UPDATE / DELETE |
| changed_by | TEXT | — | User role that made the change |
| changed_at | DATETIME | NOT NULL, DEFAULT datetime('now') | When change occurred |
| old_values | TEXT | — | JSON snapshot of old values |
| new_values | TEXT | — | JSON snapshot of new values |

---

## 5. Frontend Requirements and Specifications

### 5.1 Architecture

Vanilla HTML5/CSS3/JavaScript single-page applications served by Flask. No frontend framework. All API calls via `fetch()` with JSON. Role simulation via `X-User-Role` HTTP header, stored in `localStorage`. Consistent navigation bar with role selector across all 5 screens.

### 5.2 Screen Specifications

#### Screen 1: Real-Time Dashboard (`/`)

**Purpose:** City-wide congestion overview with interactive map  
**Key Elements:**
- **KPI Strip (4 cards):** Observations last 24h · High Congestion Events · City Avg Speed · Open Incidents — all loaded from `/api/dashboard`
- **Leaflet.js Interactive Map (primary feature):**
  - Map centred on Bengaluru (12.9716°N, 77.5946°E), OpenStreetMap tiles
  - Junction markers: **circle markers** coloured by congestion level (Red=SEVERE, Orange=HIGH, Yellow=MODERATE, Green=LOW/NORMAL, Grey=No data); radius proportional to vehicle count (`max(8, min(22, count/20))`)
  - Incident markers: **diamond icons** (rotated square via CSS `transform: rotate(45deg)`) coloured by severity
  - Click any marker → popup showing junction name, zone, congestion level, vehicle count, speed, weather
  - 60-second auto-refresh with incremental marker update (no full redraw — prevents flicker)
  - "Jump to Junction" sidebar list — click to `flyTo()` the junction with camera animation
- **Junction Status Table:** Most recent observation per junction — sortable, clickable rows fly to map
- **Zone Summary Table:** Aggregated stats per zone for last 24h (junctions, roads, observations, avg speed, open incidents)
- **Incident Severity Strip:** Open incidents grouped by severity with pill badges
- **Role Selector:** `<select>` in nav persists role to `localStorage`; updates API header on all subsequent requests

#### Screen 2: Traffic Observations (`/traffic`)

**Purpose:** Query and analyse traffic observations with filtering  
**Key Elements:**
- Filter bar: Zone dropdown → Junction cascade dropdown (reloads on zone change), Congestion Level, Hours (lookback window: 1/6/24/48/168/720h)
- Peak-hour bar chart: pure CSS div bars (no charting library) from `/api/analytics/peak-hours`
- Results table: Junction, Road, Time, Vehicles, Speed, Congestion, Weather, Data Source
- Export note for planners

#### Screen 3: Incident Management (`/incidents`)

**Purpose:** Log, view, resolve, and delete incidents  
**Key Elements:**
- **Report Incident form** (visible to officer/admin role only via `data-requires-role`):
  - Fields: Incident Type, Severity, Description, Road, Reported By (optional: Junction, Vehicle ID)
  - POST to `/api/incidents`
- **Open Incidents table:** Type, Severity, Road/Junction, Reported time, Status
- **Resolve button** (officer/admin): opens inline modal → PUT `/api/incidents/{id}` with `resolved_datetime`
- **Delete button** (admin only): DELETE `/api/incidents/{id}`
- Role-conditional rendering: public users see read-only view; officers see form + resolve; admin sees form + resolve + delete

#### Screen 4: Add Observation (`/observation`)

**Purpose:** Log a new traffic measurement at a junction  
**Key Elements:**
- Zone → Junction cascade dropdowns (dynamic load from `/api/junctions`)
- Numeric inputs: Vehicle Count, Avg Speed
- Auto-suggest Congestion Level: `vehicle_count > 200 → HIGH; speed < 25 → HIGH/SEVERE` (client-side JS hint, user can override)
- Dropdowns: Congestion Level, Weather Condition, Data Source
- POST to `/api/traffic`
- Recent 10 observations panel for the selected junction (loads from `/api/traffic?junction_id=X&hours=1`)
- Success toast notification (bottom-right, 3s)

#### Screen 5: Roads & Junctions (`/roads`)

**Purpose:** Reference data browser for road network  
**Key Elements:**
- 4-tab interface (lazy-load on first click):
  - **Roads tab:** Zone filter → paginated table (Road Name, Type, Lanes, Speed Limit, Length, Zone)
  - **Junctions tab:** Zone filter → table with coordinates, signal status, type
  - **Zones tab:** Zone summary cards (area, type, junction count, road count)
  - **Analytics tab:** Top 5 most congested junctions from `/api/analytics/top-congested`

### 5.3 Frontend Technical Constraints

- No CSS/JS framework — plain CSS with custom properties (CSS variables) for theming
- All API calls via native `fetch()` with JSON parsing
- Form validation in JS before submission; inline error display (no `alert()`)
- Role stored in `localStorage` under key `utms_role`; sent as `X-User-Role` header on every request
- Toast notification system: fixed bottom-right, type colours (blue=info, green=success, red=error)
- Responsive breakpoints for ≥768px and mobile (map grid collapses to single column)

---

## 6. Backend — API, Connectivity, and Application

### 6.1 Backend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| Web Framework | Flask | 3.0+ |
| Database | SQLite | 3.x |
| DB Connector | sqlite3 (stdlib) | — |
| Containerisation | Docker + Compose | latest |
| CI/CD | GitHub Actions | — |

### 6.2 REST API Endpoints (14 total)

#### HTML Page Routes

| Method | Endpoint | Returns | Description |
|--------|----------|---------|-------------|
| GET | `/` | HTML | Dashboard page |
| GET | `/traffic` | HTML | Traffic observations page |
| GET | `/incidents` | HTML | Incident management page |
| GET | `/observation` | HTML | Add observation page |
| GET | `/roads` | HTML | Roads & junctions reference page |

#### REST JSON Endpoints

| Method | Endpoint | Auth | Description | SQL Operation |
|--------|----------|------|-------------|---------------|
| GET | `/api/health` | Any | Health check | — |
| GET | `/api/zones` | Any | List all zones | SELECT |
| GET | `/api/roads` | Any | List roads (filter: `?zone_id=`) | SELECT + JOIN |
| GET | `/api/roads/<id>` | Any | Single road detail | SELECT + WHERE |
| GET | `/api/junctions` | Any | List junctions (filter: `?zone_id=`) | SELECT + JOIN |
| GET | `/api/traffic` | Any | List observations (filter: junction_id, road_id, hours) | SELECT + WHERE |
| GET | `/api/traffic/<road_id>` | Any | Observations for specific road | SELECT + WHERE |
| POST | `/api/traffic` | officer/admin | Add traffic observation | BEGIN → INSERT → UPDATE Junction → COMMIT |
| GET | `/api/incidents` | Any | List incidents (filter: `?open_only=true`) | SELECT + JOIN |
| GET | `/api/incidents/<id>` | Any | Single incident detail | SELECT + JOIN |
| POST | `/api/incidents` | officer/admin | Create new incident | INSERT (parameterized) |
| PUT | `/api/incidents/<id>` | officer/admin | Update/resolve incident (validates resolved > reported) | UPDATE |
| DELETE | `/api/incidents/<id>` | admin only | Delete incident | DELETE |
| GET | `/api/map` | Any | Map data: junctions with coords + open incidents with coords | SELECT + correlated subquery |
| GET | `/api/dashboard` | Any | KPIs + junction status + zone summary + incident summary | Multiple SELECT + VIEW |
| GET | `/api/analytics/peak-hours` | Any | Observations grouped by hour-of-day | SELECT + strftime() + GROUP BY |
| GET | `/api/analytics/zone-summary` | Any | Zone-level aggregates | SELECT + GROUP BY |
| GET | `/api/analytics/top-congested` | Any | Top 5 most congested junctions (last 24h) | SELECT + AVG + GROUP BY + ORDER BY + LIMIT |
| GET | `/api/audit` | admin only | Audit log entries | SELECT from Audit_Log |

**Total: 5 HTML + 14 JSON = 19 routes**

### 6.3 Database Connectivity Pattern

```python
from flask import g
import sqlite3

def get_db():
    """Per-request connection — thread-safe for SQLite."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row   # column-name dict access
        g.db.execute("PRAGMA foreign_keys = ON")   # enforce FK constraints
        g.db.execute("PRAGMA journal_mode = WAL")  # WAL for concurrency
    return g.db

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

Key design decisions:
- **Connection-per-request** (not connection pool): safe for SQLite's write-serialization model
- **`row_factory = sqlite3.Row`**: enables `row['column_name']` access → `dict(row)` serialization
- `PRAGMA foreign_keys = ON` set on **every connection** (SQLite resets this per connection)
- `PRAGMA journal_mode = WAL` enables concurrent reads during write transactions

### 6.4 Input Validation Rules

| Field | Validation |
|-------|-----------|
| junction_id / road_id | Must be INTEGER; FK check enforced by SQLite after parameterized INSERT |
| vehicle_count | Must be present and INTEGER ≥ 0 |
| avg_speed_kmph | Must be REAL ≥ 0 |
| congestion_level | Must be in `{LOW, MODERATE, HIGH, SEVERE}` |
| incident_type | Must be in `{Accident, Breakdown, Roadblock, Flooding}` |
| severity | Must be in `{LOW, MEDIUM, HIGH, CRITICAL}` |
| resolved_datetime | Must be a valid datetime AND > reported_datetime (application-layer check) |
| observation_time | Defaults to `datetime('now')` if omitted |

All validation occurs **before** any SQL execution. Missing required fields return HTTP 400 with a JSON `{"error": "Missing required fields: ..."}` body.

### 6.5 ACID Transaction Demonstration

**Scenario 1: Log Observation + Update Junction Congestion (Atomic)**

```python
db = get_db()
db.execute("BEGIN")
try:
    cursor = db.execute(
        """INSERT INTO Traffic_Observation
           (junction_id, road_id, vehicle_count, avg_speed_kmph,
            congestion_level, weather_condition, data_source, observation_time)
           VALUES (?,?,?,?,?,?,?, datetime('now'))""",
        (junction_id, road_id, vehicle_count, avg_speed_kmph,
         congestion_level, weather_condition, data_source)
    )
    obs_id = cursor.lastrowid
    # Trigger fires automatically on INSERT — updates Junction.congestion_status
    db.execute("COMMIT")
    return jsonify({'obs_id': obs_id}), 201
except sqlite3.IntegrityError as e:
    db.execute("ROLLBACK")
    return jsonify({'error': str(e)}), 400
```

**ACID Properties demonstrated:**
- **Atomicity**: BEGIN/COMMIT wraps INSERT + trigger UPDATE — either both succeed or ROLLBACK undoes both
- **Consistency**: FK constraints prevent orphan observations; CHECK constraints prevent invalid congestion values; trigger maintains derived congestion_status
- **Isolation**: SQLite WAL mode allows concurrent readers during write; write serialization prevents lost updates
- **Durability**: WAL journal ensures committed transaction survives crash; checkpoint merges WAL back to DB file

**Scenario 2: Two-Phase Locking (2PL) — Lost Update Prevention**
```
T1: BEGIN → reads Junction(1).congestion_status → writes 'HIGH'
T2: BEGIN → reads Junction(1).congestion_status → writes 'MODERATE'
Without 2PL: T2's write overwrites T1's write (lost update anomaly)
With SQLite WAL + write serialization: T2 waits for T1 to COMMIT before acquiring write lock
```

### 6.6 Triggers and Views

#### Trigger 1: `trg_congestion_alert` (AFTER INSERT on Traffic_Observation)
```sql
CREATE TRIGGER trg_congestion_alert
AFTER INSERT ON Traffic_Observation
WHEN NEW.vehicle_count > 200
BEGIN
    UPDATE Junction
    SET congestion_status = 'HIGH'
    WHERE junction_id = NEW.junction_id;
END;
```
**Purpose:** Automatically maintain derived attribute `congestion_status` — avoids application-layer update, ensures consistency.

#### Trigger 2: `trg_reset_congestion` (AFTER INSERT on Traffic_Observation)
```sql
-- Resets congestion to NORMAL when vehicle_count drops back below 100
CREATE TRIGGER trg_reset_congestion
AFTER INSERT ON Traffic_Observation
WHEN NEW.vehicle_count <= 100
BEGIN
    UPDATE Junction SET congestion_status = 'NORMAL'
    WHERE junction_id = NEW.junction_id;
END;
```

#### Trigger 3 & 4: `trg_incident_audit_insert` / `trg_incident_audit_update`
```sql
-- Audit trail: fires on every INSERT/UPDATE on Incident table
CREATE TRIGGER trg_incident_audit_insert
AFTER INSERT ON Incident
BEGIN
    INSERT INTO Audit_Log(table_name, record_id, action, changed_at, new_values)
    VALUES ('Incident', NEW.incident_id, 'INSERT', datetime('now'),
            json_object('type', NEW.incident_type, 'severity', NEW.severity));
END;
```
**Purpose:** Provides immutable audit trail for all incident data changes — supports security requirement NFR3 and accountability.

#### View: TrafficDashboard
```sql
CREATE VIEW TrafficDashboard AS
SELECT j.junction_id, j.junction_name, j.latitude, j.longitude,
       z.zone_name, z.zone_type,
       t.observation_time, t.vehicle_count, t.avg_speed_kmph,
       t.congestion_level, t.weather_condition,
       s.operational_status AS signal_status
FROM Junction j
LEFT JOIN Zone z ON j.zone_id = z.zone_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
    AND t.observation_time = (
        SELECT MAX(t2.observation_time) FROM Traffic_Observation t2
        WHERE t2.junction_id = j.junction_id
    )
LEFT JOIN Traffic_Signal s ON j.junction_id = s.junction_id;
```

### 6.7 Role-Based Access Control Implementation

```
Request → Flask route → require_role(min_role) decorator → read X-User-Role header
                                                          ↓
                                              'public' | 'officer' | 'admin'
                                                          ↓
         Role hierarchy:  admin > officer > public
         GET endpoints:   any role (including no header → defaults to 'public')
         POST/PUT:        officer or admin only → 403 if public
         DELETE:          admin only → 403 if officer or public
         /api/audit:      admin only → 403 otherwise
```

In production PostgreSQL, this would be enforced via:
```sql
CREATE ROLE public_read;
CREATE ROLE traffic_officer;
CREATE ROLE system_admin;

GRANT SELECT ON TrafficDashboard TO public_read;
GRANT INSERT, UPDATE ON Traffic_Observation TO traffic_officer;
GRANT INSERT, UPDATE ON Incident TO traffic_officer;
GRANT ALL PRIVILEGES ON ALL TABLES TO system_admin;
REVOKE DELETE ON Road, Junction, Zone FROM traffic_officer;
```

---

## 7. System Features (DBMS Concepts Demonstrated)

### 7.1 Three-Schema Architecture
External (views) → Conceptual (normalized tables) → Internal (indexes, WAL) — demonstrated live in the running system. See Section 2.1.

### 7.2 ER/EER Modeling
10 entities, 11 relationships, 2 ISA hierarchies (total-disjoint for Vehicle, partial-disjoint for Incident). Full Chen-notation specification in `docs/ER_Diagram_Specification.md`.

### 7.3 ER-to-Relational Mapping
All 7 mapping rules applied and documented in Section 4.3. ISA mapping uses separate table per subtype with shared PK.

### 7.4 Normalization (BCNF)
All 10 base tables verified in BCNF. Full functional dependency analysis and decomposition walkthrough for Traffic_Observation in Section 4.4. Lossless join and dependency preservation verified.

### 7.5 Indexing
- 7 explicit B+ tree indexes on range-query and JOIN columns
- 2 UNIQUE (hash-equivalent) indexes on high-cardinality equality columns
- Composite index `idx_obs_junction_time (junction_id, observation_time)` exploited by TrafficDashboard correlated subquery
- Index effectiveness verified via `EXPLAIN QUERY PLAN`

### 7.6 ACID Transactions and Concurrency
- Explicit `BEGIN` / `COMMIT` / `ROLLBACK` in Flask backend for all multi-step operations
- Two-Phase Locking conceptually demonstrated: growing phase (locks acquired) then shrinking phase (locks released at COMMIT)
- Write serialization in SQLite WAL prevents lost update anomaly
- Deadlock prevention: consistent lock acquisition order (Junction before Observation)

### 7.7 Recovery (WAL)
- `PRAGMA journal_mode = WAL` enables Write-Ahead Logging
- All writes go to WAL file first; DB file updated at checkpoint
- Crash mid-transaction: SQLite replays committed WAL entries, discards uncommitted
- Checkpoint demonstrated: `PRAGMA wal_checkpoint(FULL)` merges WAL back to main DB file

### 7.8 Security and RBAC
- Application-layer RBAC via `X-User-Role` header
- Public GET endpoints: no restriction
- Mutation endpoints (POST/PUT): officer or admin
- Destructive endpoints (DELETE, audit): admin only
- All SQL parameterized — no SQL injection possible
- Demonstrates SQL GRANT/REVOKE pattern for production RDBMS (Section 6.7)

### 7.9 Query Optimization
- `EXPLAIN QUERY PLAN` used to verify index usage on dashboard query
- Composite index eliminates full table scan on 720-row observation set
- Views pre-compute joins for repeated access patterns
- Correlated subquery in TrafficDashboard leverages `idx_obs_junction_time` for fast MAX(observation_time) lookup

---

## 8. External Interface Requirements

| Interface | Type | Description |
|-----------|------|-------------|
| User Interface | HTML/CSS/JS in browser | 5 screens, Leaflet.js map, vanilla fetch() |
| Map Tiles | OpenStreetMap (CDN) | Leaflet.js tile layer, no API key required |
| Backend API | REST over HTTP | JSON responses, default port 5000 |
| Database | SQLite file | `data/traffic.db`, sqlite3 stdlib |
| CI/CD | GitHub Actions | `.github/workflows/ci.yml` |
| Container | Docker + Compose | `Dockerfile` + `docker-compose.yml` |

### 8.1 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) executes on every `git push`:

```
1. Checkout code
2. Set up Python 3.12
3. Install dependencies: pip install -r requirements.txt
4. Validate SQL schema: python3 -c "import sqlite3; sqlite3.connect(':memory:').executescript(open('sql/schema.sql').read())"
5. Initialize database: python3 init_db.py
6. Run pytest: pytest tests/test_api.py -v
7. Build Docker image: docker build -t utms:test .
8. Docker smoke test: docker run → curl /api/health → assert status=ok
```

**27 pytest test cases** covering: health check, CRUD all entities, RBAC 403 responses, input validation 400 responses, HTML page routes, dashboard structure, map data coordinates, analytics endpoints.

### 8.2 Containerisation

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python init_db.py
EXPOSE 5000
ENV FLASK_APP=app/app.py
CMD ["flask", "run", "--host=0.0.0.0"]
```

---

## 9. Validation and Verification

### 9.1 Automated Test Suite

27 pytest tests in `tests/test_api.py`:

| Test ID | Category | Description | Expected Result |
|---------|----------|-------------|-----------------|
| T1 | Health | GET /api/health | 200, `{"status":"ok"}` |
| T2 | Read | GET /api/zones | 200, 5 zones, includes Whitefield |
| T3 | Read | GET /api/roads | 200, ≥ 10 roads |
| T4 | Filter | GET /api/roads?zone_id=1 | 200, all rows have zone_id=1 |
| T5 | Read | GET /api/junctions | 200, ≥ 10 junctions |
| T6 | Read | GET /api/traffic?hours=720 | 200, ≥ 50 observations |
| T7 | ACID Write | POST /api/traffic (officer) | 201, `obs_id` > 0 returned |
| T8 | RBAC | POST /api/traffic (no role) | 403 Forbidden |
| T9 | Validation | POST /api/traffic (missing road_id) | 400, "Missing required fields" |
| T10 | FK/Rollback | POST /api/traffic (junction_id=9999) | 400, FK violation → ROLLBACK |
| T11 | Filter | GET /api/incidents?open_only=true | 200, all rows have resolved_datetime=null |
| T12 | Create | POST /api/incidents (officer) | 201, `incident_id` returned |
| T13 | Update | PUT /api/incidents/{id} (resolve) | 200 |
| T14 | Validation | PUT /api/incidents/{id} (resolved < reported) | 400 |
| T15 | RBAC Delete | DELETE /api/incidents/{id} (admin) | 200 then 404 on GET |
| T16 | RBAC | DELETE /api/incidents/1 (officer) | 403 Forbidden |
| T17 | Dashboard | GET /api/dashboard | 200, has junctions/zones/city_kpis/incident_summary |
| T18 | Map | GET /api/map | 200, junctions have lat/lon not null, incidents present |
| T19 | Analytics | GET /api/analytics/peak-hours | 200, ≤ 24 hour buckets |
| T20 | Analytics | GET /api/analytics/top-congested | 200, ≤ 5 rows |
| T21 | Audit (Admin) | GET /api/audit (admin) | 200 |
| T22 | Audit (Public) | GET /api/audit (no role) | 403 |
| T23–T27 | HTML pages | GET /, /traffic, /incidents, /observation, /roads | 200, contains "Urban Traffic" |

### 9.2 Manual Verification Test Cases

| Test | Steps | Expected Outcome |
|------|-------|-----------------|
| Trigger fires | Insert observation with vehicle_count=250, then SELECT congestion_status | Junction.congestion_status = 'HIGH' |
| WAL recovery | Kill process mid-transaction, restart, query | DB at last committed state; partial write discarded |
| EXPLAIN plan | `EXPLAIN QUERY PLAN SELECT ... FROM Traffic_Observation WHERE junction_id=1 AND observation_time > ...` | Shows `SEARCH Traffic_Observation USING INDEX idx_obs_junction_time` |
| 4-table JOIN | Dashboard query (Junction–TrafficDashboard–Zone–Signal) | Executes < 1 second on seed dataset |
| RBAC enforcement | Switch role to Public in nav, attempt POST /api/incidents | Toast shows "403 — Insufficient permissions" |
| FK cascade | Attempt DELETE on Junction that has Traffic_Observations | Rejected with FK constraint error |
| ISA subtype | Insert into Vehicle then Car with same vehicle_id | Both rows inserted; JOIN returns combined attributes |

---

## 10. Work-Integrated Activities Mapping

This section maps each required Work-Integrated Activity (WIA 1–5) to the project deliverables.

| WIA | Topic | Project Coverage | Deliverable Location |
|-----|-------|-----------------|----------------------|
| **WIA 1** | Conceptual Model — ER/EER Diagram | 10-entity EER diagram with 11 relationships, 2 ISA hierarchies (Vehicle total-disjoint, Incident partial-disjoint) | `docs/ER_Diagram_Specification.md` — full Chen notation spec with AI image prompt |
| **WIA 2** | Logical Design — Tables in 3NF/BCNF, FDs, Decomposition | All 10 base tables verified BCNF; full FD analysis and decomposition walkthrough for Traffic_Observation; lossless join and dependency preservation verified | Section 4.3 and 4.4 of this SRS; `sql/schema.sql` |
| **WIA 3** | Physical Design — Index Design, B+ Tree, Hashing | 7 B+ tree indexes (time-series, JOIN columns) + 2 hash-equivalent UNIQUE indexes (license_plate, license_no); composite index rationale; B+ vs Hash comparison | Section 4.5 of this SRS; `sql/schema.sql` (CREATE INDEX statements) |
| **WIA 4** | DB Administration — Transactions, Concurrency, Recovery | ACID demonstration (BEGIN/COMMIT/ROLLBACK in app.py); 2PL commentary; WAL recovery scenario; concurrent read/write with WAL mode | Section 6.5–6.6; `sql/triggers.sql` (transaction demos); `app/app.py` |
| **WIA 5** | Security — Role-Based Access, GRANT/REVOKE | 3-tier RBAC (Admin/Officer/Public) enforced in Flask middleware; SQL GRANT/REVOKE pattern documented for production PostgreSQL migration; audit trigger logs all changes | Section 6.7; `app/app.py` (require_role); `sql/triggers.sql` (audit triggers) |

### Syllabus Coverage Summary

| Module | Topic | Coverage |
|--------|-------|----------|
| M1 | DBMS Concepts | Three-schema architecture (§2.1), data independence |
| M2 | ER/EER Modeling | 10 entities, 2 ISA hierarchies, aggregation (§4.1, `docs/ER_Diagram_Specification.md`) |
| M2 | Relational Model | 7-rule ER-to-Relational mapping (§4.3) |
| M3 | Relational Algebra | Queries in `sql/triggers.sql` demonstrate σ, π, ⋈ |
| M3 | SQL | 20+ queries: JOINs, GROUP BY, subqueries, views, triggers (`sql/`) |
| M4 | Normalization | BCNF proof for all 10 tables; FD analysis (§4.4) |
| M5 | Indexing | B+ tree + hash-equivalent indexes; EXPLAIN QUERY PLAN (§4.5) |
| M6 | Transactions | ACID demo, 2PL, WAL recovery (§6.5, §7.6, §7.7) |
| M7 | Security | RBAC, GRANT/REVOKE, parameterized SQL (§6.7, §7.8) |
| M8 | Query Optimization | EXPLAIN plan, index selectivity, composite index rationale (§7.9) |

---

## 11. Appendix

### 11.1 Use Case Models

**UC1: Log Traffic Observation**
- Actor: Traffic Officer
- Precondition: Officer role selected; junction and road exist in DB
- Main Flow: Open `/observation` → Select zone → Select junction → Enter vehicle count, speed, congestion → Submit → POST /api/traffic → BEGIN TRANSACTION → INSERT Traffic_Observation → Trigger updates Junction.congestion_status → COMMIT → Success toast
- Alternate: Invalid junction_id → FK violation → ROLLBACK → 400 response → error toast

**UC2: View Congestion Dashboard**
- Actor: Any user (Public)
- Flow: Load `/` → JS calls `/api/map` and `/api/dashboard` → Leaflet.js renders circle markers → User clicks junction → Popup shows latest observation → User clicks junction list → Map flies to location with camera animation
- Data: Served from TrafficDashboard view (External Schema)

**UC3: Report Incident**
- Actor: Traffic Officer
- Flow: Navigate to `/incidents` → Fill incident form → POST /api/incidents → Record created with reported_datetime = now → Row appears in Open Incidents table → Audit trigger fires → Log entry created in Audit_Log

**UC4: Resolve Incident**
- Actor: Traffic Officer / Admin
- Flow: View open incidents → Click Resolve → Modal accepts resolved_datetime → PUT /api/incidents/{id} → Application validates resolved_datetime > reported_datetime → UPDATE executed → Incident moves to resolved state

**UC5: Admin Deletes Incident**
- Actor: Admin
- Flow: Switch role to Admin → Open Incidents table shows Delete button → DELETE /api/incidents/{id} → Confirmed → 200 response → Row removed → Audit trigger creates DELETE log entry

**UC6: City Planner Analyses Congestion**
- Actor: City Planner
- Flow: Navigate to `/traffic` → Set date range, zone, congestion level filter → GET /api/traffic → Table shows filtered observations → Scroll to peak-hour bar chart → Identify peak congestion hours by zone

### 11.2 Viva Preparation — Expected Hard Questions

| # | Question | Answer Summary |
|---|----------|----------------|
| 1 | Why B+ tree over hash index for junction lookups? | Dashboard query uses range scan (`WHERE observation_time BETWEEN ...`) and ORDER BY — hash index doesn't support range queries. B+ tree leaf nodes form a linked list enabling O(range) sequential scan. |
| 2 | Demonstrate a lost update without 2PL. | T1 reads Junction(1) congestion=NORMAL, T2 reads Junction(1) congestion=NORMAL. T1 writes HIGH. T2 writes MODERATE (overwrites T1's HIGH — lost update). SQLite WAL serializes writes: T2 blocks until T1 commits. |
| 3 | Walk through BCNF decomposition of Traffic_Observation. | obs_id→{junction_id,road_id,...} (OK); junction_id→junction_name (transitive — not BCNF). Decompose: remove junction_name, keep junction_id FK. Verify lossless join on R1∩R2={junction_id} (functional dependency holds). |
| 4 | How does WAL recovery handle a crash mid-transaction? | WAL writes changes to wal file before DB file. On crash: uncommitted changes are only in WAL, never in DB. On restart: SQLite reads WAL, finds no COMMIT for in-flight transaction, discards it. DB is at last committed checkpoint. |
| 5 | What schema changes needed for Term 2 spatial data? | Add `geometry BLOB` to Junction (PostGIS point); add `geom_linestring` to Road. Create R-tree spatial index. Query: `ST_DWithin(j.geometry, origin_point, 1000)` for junctions within 1km. Migrate to PostgreSQL+PostGIS. |
| 6 | Why B+ tree over B-tree for timestamp index? | B-tree stores data at all levels (internal + leaf). B+ tree stores data only at leaves, with leaf nodes linked. For timestamp range queries, B+ tree supports sequential leaf scan without backtracking — O(k) for k results vs O(k log n) for B-tree. |
| 7 | Show a query that uses your index vs one that does a full table scan. | Uses index: `SELECT * FROM Traffic_Observation WHERE junction_id=3 ORDER BY observation_time DESC LIMIT 10` (EXPLAIN QUERY PLAN: USING INDEX idx_obs_junction_time). Full scan: `SELECT * FROM Traffic_Observation WHERE weather_condition='Rainy'` (no index on weather_condition). |

### 11.3 Future Enhancements (Term 2)

- **PostGIS / Spatial:** Add geometry column to Junction and Road; `ST_Distance`, `ST_Intersects` queries
- **R-Tree spatial indexing:** For road-network proximity queries (find junctions within X km)
- **TimescaleDB / Partitioning:** Partition Traffic_Observation by month for time-series efficiency
- **Traffic camera image storage:** File path in DB + BLOB thumbnail
- **Real-time sensor ingestion:** WebSocket server pushing live observations
- **Migration to PostgreSQL:** Enables true multi-user concurrency, stored procedures, full GRANT/REVOKE

### 11.4 Project File Structure

```
Urban_Traffic_Management_System/
├── app/
│   ├── app.py                    # Flask REST API (19 routes, ACID, RBAC)
│   ├── templates/
│   │   ├── index.html            # Dashboard with Leaflet.js map
│   │   ├── traffic.html          # Traffic observations + peak-hour chart
│   │   ├── incidents.html        # Incident management
│   │   ├── observation.html      # Add observation form
│   │   └── roads_junctions.html  # Roads & junctions reference
│   └── static/
│       ├── css/style.css         # Custom CSS with variables
│       └── js/app.js             # Shared fetch/role/toast utilities
├── sql/
│   ├── schema.sql                # DDL: 10 tables + 8 ISA subtypes + audit
│   ├── seed_data.sql             # Bengaluru: 5 zones, 20 roads, 15 junctions
│   └── triggers.sql             # 4 triggers + 3 views + ACID demo scripts
├── tests/
│   └── test_api.py               # 27 pytest tests
├── docs/
│   ├── SRS.md                    # This document
│   └── ER_Diagram_Specification.md  # Chen ER notation + AI image prompt
├── .github/workflows/ci.yml      # GitHub Actions CI pipeline
├── Dockerfile                    # Python 3.12-slim container
├── docker-compose.yml            # Single-service compose file
├── init_db.py                    # DB initializer (schema → triggers → seed)
└── requirements.txt              # Flask==3.0.3, pytest==8.4.2
```

### 11.5 Document History

| Version | Date | Description |
|---------|------|-------------|
| 0.1 | Sep 2026 | Initial draft — problem statement and scope |
| 1.0 | Oct 2026 | Complete SRS per IEEE 830 / ISO/IEC/IEEE 29148 |
| 2.0 | Oct 2026 | Updated: actual 14 API endpoints, Leaflet.js map, WIA mapping, viva prep, CI/CD, audit trigger, 27 test cases, complete BCNF table, file structure |

---

*Prepared by: Nimisha Gupta | BITS Pilani WILP | SESAP ZC337 | October 2026*  
*Lab Session 2 Submission — Prototype + SRS | Deadline: 17 October 2026*
