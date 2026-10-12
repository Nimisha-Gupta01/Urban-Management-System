# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## Urban Road & Real-Time Traffic Information and Management Database System

**Document Version:** 3.0  
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
**Term 1 Scope:** Fully normalized relational database, REST API backend, interactive Streamlit frontend with live map, containerised deployment with Docker Compose.

The system enables:
- Storage and retrieval of road and junction network data
- Real-time (simulated) traffic observation logging
- Incident registration, tracking, and resolution
- Traffic signal status management
- Vehicle and driver registration
- Congestion analytics by zone, time window, and road segment
- Interactive Folium map showing live congestion and incidents
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
| RBAC | Role-Based Access Control |
| WAL | Write-Ahead Log |
| WIA | Work-Integrated Activity |
| ORM | Object-Relational Mapping |

### 1.4 References

- IEEE 830-1998: IEEE Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2018: Systems and Software Engineering — Life Cycle Processes — Requirements Engineering
- Elmasri & Navathe, *Fundamentals of Database Systems*, 7th Edition, Pearson
- PostgreSQL 16 Documentation: https://www.postgresql.org/docs/16/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- BITS Pilani SESAP ZC337 Lab Assignment Handout, Version 1.0, September 2026
- Project Schema: `sql/schema.sql`
- Triggers and Views: `sql/triggers.sql`

---

## 2. Overall Description

### 2.1 Product Perspective

The Urban Traffic Management System is a three-tier web application:

```
┌─────────────────────────────────────────────┐
│  Presentation Tier (Frontend)               │
│  Streamlit (Python)                         │
│  6 pages: Home, Dashboard (Folium map),     │
│  Traffic Observations, Add Observation,     │
│  Incident Management, Roads & Zones         │
└────────────────────┬────────────────────────┘
                     │ HTTP REST (JSON)
                     │ requests library + X-User-Role header
┌────────────────────▼────────────────────────┐
│  Application Tier (Backend)                 │
│  Python FastAPI + Uvicorn                   │
│  20+ endpoints, parameterized SQL,          │
│  ACID transactions, RBAC middleware         │
└────────────────────┬────────────────────────┘
                     │ psycopg2 / asyncpg
                     │ PostgreSQL wire protocol
┌────────────────────▼────────────────────────┐
│  Data Tier (Database)                       │
│  PostgreSQL 16                              │
│  13 tables + 8 ISA subtype tables,          │
│  3 views, 4 triggers, stored procedure,     │
│  9 indexes, 1 audit log table               │
└─────────────────────────────────────────────┘
```

This architecture implements the **Three-Schema Architecture** (ANSI/SPARC):

| Schema Level | Implementation |
|---|---|
| **External Schema** | SQL VIEWs: `v_junction_live_status`, `v_zone_summary`, `v_incident_report` — each user role sees a tailored view of the data |
| **Conceptual Schema** | 13 normalized tables in BCNF: Zone, Road, Junction, Road_Junction, Traffic_Signal, Driver, Vehicle, Incident, Incident_Audit, Traffic_Observation, Sensor + ISA subtype tables |
| **Internal Schema** | Physical storage via PostgreSQL: 9 B-tree indexes, WAL (Write-Ahead Log) default journal, heap storage with MVCC |

### 2.2 Product Functions

| Function | Description |
|----------|-------------|
| Road Network Management | Store and query roads, junctions, zones, and their relationships |
| Traffic Observation Logging | Record vehicle count, average speed, congestion level at junctions |
| Incident Management | Log, update, resolve, and delete traffic incidents |
| Signal Management | Track traffic signal status, timing, and operational health |
| Vehicle & Driver Registry | Maintain vehicle registrations linked to driver/owner details |
| Congestion Analytics | Aggregate reports by zone, time range, road segment; peak-hour analysis |
| Live Congestion Map | Folium interactive map showing junction congestion (colour-coded) and open incidents |
| Role-Based Access | Enforce Admin / Traffic Officer / Public access tiers |
| Data Integrity | PK/FK constraints, triggers, CHECK constraints, NOT NULL rules |
| Audit Logging | Automatic audit trail of all incident severity changes via AFTER trigger |
| ACID Transactions | Explicit transaction management for all multi-step operations |
| WAL Recovery | PostgreSQL WAL ensuring durability and point-in-time recovery |

### 2.3 User Characteristics

| User Role | Description | Access Level | Technical Level |
|-----------|-------------|--------------|-----------------|
| System Admin | Manages schema, users, roles, backups; can delete records | Full DDL + DML | High |
| Traffic Officer / Control Room | Logs incidents and observations; can resolve incidents | INSERT + UPDATE + SELECT | Medium |
| City Planner / Municipal Authority | Generates reports, analyses congestion | SELECT only | Low–Medium |
| Emergency Services | Queries incidents and fastest-route data | SELECT only | Low |
| Commuter (Public) | Views congestion and signal status | SELECT (public views only) | Low |

### 2.4 Constraints

- Database MUST be implemented in **PostgreSQL 16** (production-grade RDBMS)
- All tables MUST be in **BCNF** (with documented justification)
- All referential integrity MUST be enforced via **FOREIGN KEY constraints**
- Backend MUST use **parameterized SQL** — no string concatenation in queries
- Frontend MUST be implemented in **Streamlit** — Python-based, multi-page app
- System MUST demonstrate **ACID properties** through explicit transaction scenarios
- Role enforcement via `X-User-Role` HTTP header (simulating authentication layer)
- All services run in **Docker containers** via Docker Compose

### 2.5 Assumptions and Dependencies

- Data scope is limited to Bengaluru for Term 1 (5 zones, 15 junctions, 20 roads seeded)
- Real-time sensor data is simulated via `init_db.py` seeding
- PostgreSQL 16 running as Docker service (or locally)
- Python 3.11+ with FastAPI 0.110+, Streamlit 1.35+
- GitHub repository used for version control
- Docker Desktop for containerised deployment
- Folium loaded from Python package — map tiles from CartoDB Positron (light)

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
| FR13 | Auto-update junction congestion_status via PostgreSQL trigger when vehicle_count changes | ✓ Implemented |
| FR14 | Auto-audit all incident severity modifications via AFTER UPDATE trigger into Incident_Audit table | ✓ Implemented |
| FR15 | Provide real-time dashboard view aggregating latest observations per junction | ✓ Implemented |
| FR16 | Support congestion reporting by zone and time window | ✓ Implemented |
| FR17 | Support incident search by road, junction, type, severity, and date range | ✓ Implemented |
| FR18 | Provide interactive map showing junction congestion (colour-coded) and open incidents | ✓ Implemented |
| FR19 | Enforce role-based access (Admin, TrafficOfficer, Public) via application-layer RBAC | ✓ Implemented |
| FR20 | Support full CRUD operations on traffic observations and incidents via REST API | ✓ Implemented |
| FR21 | Return all API responses in JSON format with appropriate HTTP status codes | ✓ Implemented |
| FR22 | Validate all API inputs before executing SQL; reject malformed requests with 400/422 | ✓ Implemented |
| FR23 | Demonstrate ACID transactions (observation insert + junction congestion update atomically) | ✓ Implemented |
| FR24 | Provide recovery demonstration via PostgreSQL WAL | ✓ Implemented |
| FR25 | Provide peak-hour analytics endpoint grouping observations by hour of day | ✓ Implemented |
| FR26 | Provide stored procedure `sp_resolve_incident` for atomic incident resolution + audit | ✓ Implemented |

### 3.2 Non-Functional Requirements

| ID | Category | Requirement | Status |
|----|----------|-------------|--------|
| NFR1 | Performance | Single-table SELECT queries shall complete in < 2 seconds for up to 10,000 records | ✓ |
| NFR2 | Performance | Multi-table JOIN queries (≤ 5 tables) shall complete in < 3 seconds for ≤ 1,000 records | ✓ |
| NFR3 | Security | Only users with Admin role may execute DELETE on incidents | ✓ |
| NFR4 | Security | Traffic Officer may INSERT/UPDATE observations and incidents; cannot DELETE records | ✓ |
| NFR5 | Security | Public role may only execute GET on public read endpoints | ✓ |
| NFR6 | Reliability | Database shall enforce NOT NULL and CHECK constraints to prevent corrupt records | ✓ |
| NFR7 | Reliability | All foreign key constraints shall be active | ✓ |
| NFR8 | Scalability | Schema shall support growth to 100,000 traffic observations and 50,000 vehicles | ✓ |
| NFR9 | Maintainability | All tables shall be in BCNF; documented in Section 4.3 | ✓ |
| NFR10 | Recoverability | Database shall recover to consistent state after simulated crash using PostgreSQL WAL | ✓ |
| NFR11 | Indexing | Composite B-tree index on (junction_id, observation_time) for fast time-series queries | ✓ |
| NFR12 | Indexing | UNIQUE index on license_plate for O(log n) vehicle lookups | ✓ |
| NFR13 | Portability | Application shall run in Docker containers (3 services) on any Linux/macOS host | ✓ |
| NFR14 | Traceability | All SQL queries shall use parameterized statements (no raw string interpolation) | ✓ |

### 3.3 Domain Requirements

- Traffic observation data complies with BBMP (Bruhat Bengaluru Mahanagara Palike) road network classification
- Incident severity must be one of: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Congestion level must be one of: `LOW`, `MODERATE`, `HIGH`, `SEVERE`
- Vehicle type must be one of: `Car`, `Truck`, `Motorcycle`, `Bus`, `Auto`, `Other`
- Speed limit values must be between 10 and 120 km/h
- Junction coordinates must be valid Bengaluru GPS coordinates (lat: 12.7–13.2, lon: 77.4–77.8)
- All timestamps stored in PostgreSQL `TIMESTAMP` format

---

## 4. Database Design

### 4.1 Three-Schema Architecture Detail

#### External Schema — SQL Views

Three views provide role-appropriate external schemas:

**v_junction_live_status** (Public + Officer): Latest observation per junction joined with zone and signal data:
```sql
CREATE OR REPLACE VIEW v_junction_live_status AS
SELECT j.junction_id, j.junction_name, z.zone_name, z.zone_type,
       t.observation_time, t.vehicle_count, t.avg_speed_kmph,
       t.congestion_level, t.weather_condition,
       s.operational_status AS signal_status
FROM Junction j
LEFT JOIN Zone z ON j.zone_id = z.zone_id
LEFT JOIN LATERAL (
    SELECT * FROM Traffic_Observation t2
    WHERE t2.junction_id = j.junction_id
    ORDER BY t2.observation_time DESC LIMIT 1
) t ON TRUE
LEFT JOIN Traffic_Signal s ON j.junction_id = s.junction_id;
```

**v_zone_summary** (Planner): Aggregated statistics per zone over the last 24 hours.

**v_incident_report** (Officer + Admin): Open incidents joined with road and junction names.

#### Conceptual Schema — 13 Normalized Tables

See Section 4.6 (Data Dictionary) for full column definitions.

#### Internal Schema — Physical Storage

- **File organization:** PostgreSQL heap files with MVCC (Multi-Version Concurrency Control)
- **Journaling:** WAL (Write-Ahead Log) — PostgreSQL default
- **Page size:** 8192 bytes (PostgreSQL default)
- **Indexes:** 9 named B-tree indexes
- **MVCC:** Allows concurrent readers never blocking writers (unlike SQLite's write serialization)

### 4.2 ER / EER Conceptual Model

The conceptual model uses **EER (Enhanced Entity-Relationship)** notation:

- **10 strong entity types** (no weak entities)
- **2 EER specialisation hierarchies** (ISA)
- **1 M:N relationship** resolved via associative/bridge entity
- **11 binary relationships** total

> **ER Diagram:** See `docs/ER_Diagram.png`

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
| 9 | INCIDENT_AUDIT | audit_id | Immutable audit log for incident changes (trigger-populated) |
| 10 | TRAFFIC_OBSERVATION | obs_id | Timestamped traffic measurement at a junction |
| 11 | SENSOR | sensor_id | Physical sensing device installed at a junction |

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
**Partial participation** (INCIDENT): some incidents may not belong to any subtype.  
**Disjoint**: a vehicle cannot be both a Car and a Truck.

### 4.3 ER-to-Relational Mapping (All 7 Rules Applied)

**Rule 1 — Regular (Strong) Entity Types:**

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

**Rule 2 — Weak Entity Types:** Not applicable — all entities have surrogate PKs (SERIAL).

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
```
Road_Junction(road_id PK+FK→Road, junction_id PK+FK→Junction, position_type)
```

**Rule 6 — Multivalued Attributes:** Not applicable.

**Rule 7 — N-ary Relationships:** Not applicable.

**ISA Mapping (one table per subtype, shared PK):**
```
Vehicle_Car(vehicle_id PK+FK→Vehicle, num_doors, fuel_type)
Vehicle_Truck(vehicle_id PK+FK→Vehicle, max_load_tonnes)
Vehicle_Motorcycle(vehicle_id PK+FK→Vehicle, engine_cc)
Vehicle_Bus(vehicle_id PK+FK→Vehicle, seating_capacity)

Incident_Accident(incident_id PK+FK→Incident, injuries, fatalities)
Incident_Breakdown(incident_id PK+FK→Incident, breakdown_cause)
Incident_Roadblock(incident_id PK+FK→Incident, authority_name)
Incident_Flooding(incident_id PK+FK→Incident, water_level_cm)
```

**Audit Table (system table, trigger-populated):**
```
Incident_Audit(audit_id PK, incident_id, action, old_severity, new_severity,
               changed_at, changed_by)
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
- All attributes atomic, no repeating groups — ✓ 1NF satisfied

**Step 2 — Second Normal Form (2NF):**
- PK is `obs_id` (single-attribute) — no partial dependency possible — ✓ 2NF automatically satisfied

**Step 3 — Third Normal Form (3NF):**
- Functional Dependencies identified:
  - `obs_id → {junction_id, road_id, observation_time, vehicle_count, ...}` ✓
  - `junction_id → {junction_name, zone_id}` — **transitive dependency detected!**
  - `road_id → road_name` — **transitive dependency detected!**
- Resolution: Remove `junction_name`, `zone_id`, `road_name` from Traffic_Observation; retain FKs only.
- Result: ✓ 3NF achieved after decomposition

**Step 4 — Boyce-Codd Normal Form (BCNF):**
- After decomposition, `obs_id` is the only determinant for all non-key attributes
- No non-trivial FD where LHS is not a superkey remains
- Result: ✓ BCNF verified

**Lossless Join:** Decomposition of R(obs_id, junction_id, junction_name) into R1(obs_id, junction_id) and R2(junction_id, junction_name): R1 ∩ R2 = {junction_id}; `junction_id → junction_name` holds → lossless ✓

#### BCNF Verification — All Tables

| Table | 1NF | 2NF | 3NF | BCNF | Justification |
|-------|-----|-----|-----|------|---------------|
| Zone | ✓ | ✓ | ✓ | ✓ | Single PK, no transitive dependencies |
| Road | ✓ | ✓ | ✓ | ✓ | zone_id is FK, not transitive from road_id |
| Junction | ✓ | ✓ | ✓ | ✓ | zone_id is FK; lat/lon determined by junction_id |
| Road_Junction | ✓ | ✓ | ✓ | ✓ | Composite PK; position_type determined by full PK |
| Traffic_Signal | ✓ | ✓ | ✓ | ✓ | Single PK; junction_id is FK |
| Driver | ✓ | ✓ | ✓ | ✓ | license_no is candidate key (UNIQUE), not transitive |
| Vehicle | ✓ | ✓ | ✓ | ✓ | license_plate is candidate key; owner_id is FK |
| Incident | ✓ | ✓ | ✓ | ✓ | All non-key attrs depend solely on incident_id |
| Traffic_Observation | ✓ | ✓ | ✓ | ✓ | Full walkthrough above |
| Sensor | ✓ | ✓ | ✓ | ✓ | junction_id is FK; all attrs depend on sensor_id |
| Incident_Audit | ✓ | ✓ | ✓ | ✓ | audit_id PK; all attrs determined by audit_id |

### 4.5 Physical Design — Indexing Strategy

#### B-Tree Indexes (Range Queries and Join Optimization)

| Index Name | Table | Column(s) | Query Pattern | Justification |
|-----------|-------|-----------|---------------|---------------|
| `idx_obs_junction_time` | Traffic_Observation | (junction_id, observation_time) | Dashboard: latest obs per junction | Composite covering index; left-prefix for junction filter, right-prefix for time range |
| `idx_obs_road` | Traffic_Observation | road_id | Filter observations by road segment | Avoids full scan on road-level queries |
| `idx_incident_road` | Incident | road_id | Incident search by road | JOIN optimization |
| `idx_incident_junction` | Incident | junction_id | Incident search by junction | JOIN optimization |
| `idx_incident_datetime` | Incident | reported_datetime | Date-range incident queries | Range scan using B-tree leaf-link list |
| `idx_road_zone` | Road | zone_id | Zone-filtered road listing | JOIN on zone_id |
| `idx_junction_zone` | Junction | zone_id | Zone-filtered junction listing | JOIN on zone_id |

#### Hash-Equivalent Indexes (Exact Equality Lookups)

| Index Name | Table | Column | Mechanism | Justification |
|-----------|-------|--------|-----------|---------------|
| `idx_vehicle_plate` | Vehicle | license_plate | UNIQUE constraint → implicit B-tree | Vehicle lookup by plate: equality only, O(log n) |
| `idx_driver_license` | Driver | license_no | UNIQUE constraint → implicit B-tree | License number lookup for driver verification |

#### B-Tree vs Hash — Design Rationale

**B-Tree chosen for time-series and range queries:**
- Supports `WHERE observation_time BETWEEN t1 AND t2` via linked leaf list
- Supports `ORDER BY observation_time DESC` without extra sort
- PostgreSQL MVCC works best with B-tree indexes (visibility maps)

**UNIQUE index for plate/license lookups:**
- Only equality predicates: `WHERE license_plate = 'KA-01-AB-1234'`
- No range queries on these columns
- PostgreSQL UNIQUE constraint creates implicit B-tree index with O(log n) lookup

### 4.6 Data Dictionary

#### Table: Zone

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| zone_id | SERIAL | PK | Auto-increment zone identifier |
| zone_name | TEXT | NOT NULL, UNIQUE | Name (e.g., "Whitefield") |
| city | TEXT | NOT NULL DEFAULT 'Bengaluru' | City name |
| area_sqkm | REAL | CHECK (area_sqkm > 0) | Zone area in km² |
| zone_type | TEXT | CHECK IN ('Residential','Commercial','Industrial','Mixed','Government') | Zone classification |

#### Table: Road

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| road_id | SERIAL | PK | Auto-increment road identifier |
| road_name | TEXT | NOT NULL | Full road name |
| road_type | TEXT | CHECK IN ('National Highway','State Highway','City Road','Lane','Ring Road','Flyover') | Road classification |
| length_km | REAL | CHECK (length_km > 0) | Road segment length in km |
| num_lanes | INTEGER | CHECK (num_lanes > 0) | Number of lanes |
| speed_limit | INTEGER | CHECK BETWEEN 10 AND 120 | Speed limit in km/h |
| surface_type | TEXT | — | Asphalt / Concrete / Gravel |
| direction_type | TEXT | — | One-way / Two-way / Divided |
| zone_id | INTEGER | FK → Zone.zone_id NOT NULL | Zone this road belongs to |

#### Table: Junction

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| junction_id | SERIAL | PK | Auto-increment junction identifier |
| junction_name | TEXT | NOT NULL | Name (e.g., "Silk Board Junction") |
| junction_type | TEXT | CHECK IN ('Signalised','Unsignalised','Roundabout','Flyover','Interchange') | Junction classification |
| latitude | REAL | CHECK BETWEEN 12.7 AND 13.2 | GPS latitude |
| longitude | REAL | CHECK BETWEEN 77.4 AND 77.8 | GPS longitude |
| signal_controlled | INTEGER | DEFAULT 0 | 0 = No, 1 = Yes |
| congestion_status | TEXT | DEFAULT 'LOW' | LOW/MODERATE/HIGH/SEVERE — auto-updated by trigger |
| zone_id | INTEGER | FK → Zone.zone_id NOT NULL | Zone this junction belongs to |

#### Table: Road_Junction

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| road_id | INTEGER | PK (composite), FK → Road | Road in the pairing |
| junction_id | INTEGER | PK (composite), FK → Junction | Junction in the pairing |
| position_type | TEXT | — | Start / End / Intermediate |

#### Table: Traffic_Signal

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| signal_id | SERIAL | PK | Auto-increment signal identifier |
| junction_id | INTEGER | FK → Junction NOT NULL | Junction where installed |
| signal_type | TEXT | — | Standard / Adaptive / Pedestrian |
| installed_date | DATE | — | Date first installed |
| operational_status | TEXT | CHECK IN ('Active','Inactive','Faulty','Under Maintenance') | Current status |
| green_duration_sec | INTEGER | CHECK (> 0) | Green phase duration in seconds |

#### Table: Driver

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| driver_id | SERIAL | PK | Auto-increment driver identifier |
| name | TEXT | NOT NULL | Full legal name |
| license_no | TEXT | UNIQUE NOT NULL | Driving license number (candidate key) |
| dob | DATE | — | Date of birth |
| contact | TEXT | — | Phone number |
| address | TEXT | — | Residential address |

#### Table: Vehicle

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| vehicle_id | SERIAL | PK | Auto-increment vehicle identifier |
| license_plate | TEXT | UNIQUE NOT NULL | Registration number, e.g., KA-01-AB-1234 |
| vehicle_type | TEXT | CHECK IN ('Car','Truck','Motorcycle','Bus','Auto','Other') | Vehicle classification |
| make | TEXT | — | Manufacturer (Maruti, Tata, etc.) |
| model | TEXT | — | Model name |
| year | INTEGER | CHECK BETWEEN 1990 AND 2030 | Manufacturing year |
| registered_state | TEXT | — | State of registration |
| owner_id | INTEGER | FK → Driver.driver_id | Owner/driver reference (nullable) |

#### Table: Incident

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| incident_id | SERIAL | PK | Auto-increment incident identifier |
| incident_type | TEXT | NOT NULL | Accident / Breakdown / Roadblock / Flooding |
| severity | TEXT | CHECK IN ('LOW','MEDIUM','HIGH','CRITICAL') | Severity rating |
| description | TEXT | — | Free-text description |
| reported_datetime | TIMESTAMP | NOT NULL DEFAULT NOW() | When reported |
| resolved_datetime | TIMESTAMP | — | When resolved; NULL = open |
| road_id | INTEGER | FK → Road (nullable) | Road where occurred |
| junction_id | INTEGER | FK → Junction (nullable) | Junction at incident site |
| vehicle_id | INTEGER | FK → Vehicle (nullable) | Vehicle involved |
| reported_by | TEXT | — | Reporting party |

#### Table: Incident_Audit

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| audit_id | SERIAL | PK | Auto-increment audit identifier |
| incident_id | INTEGER | NOT NULL | Reference to Incident (no FK to allow orphan audit entries) |
| action | TEXT | NOT NULL | INSERT / UPDATE / DELETE |
| old_severity | TEXT | — | Severity before change |
| new_severity | TEXT | — | Severity after change |
| changed_at | TIMESTAMP | NOT NULL DEFAULT NOW() | When change occurred |
| changed_by | TEXT | — | User role that made the change |

#### Table: Traffic_Observation

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| obs_id | SERIAL | PK | Auto-increment observation identifier |
| junction_id | INTEGER | FK → Junction NOT NULL | Junction being observed |
| road_id | INTEGER | FK → Road NOT NULL | Road segment being observed |
| observation_time | TIMESTAMP | NOT NULL DEFAULT NOW() | Timestamp |
| vehicle_count | INTEGER | CHECK (>= 0) | Vehicles counted |
| avg_speed_kmph | REAL | CHECK (>= 0) | Average speed in km/h |
| congestion_level | TEXT | CHECK IN ('LOW','MODERATE','HIGH','SEVERE') | Congestion classification |
| weather_condition | TEXT | — | Clear / Rainy / Foggy / Cloudy / Stormy |
| data_source | TEXT | — | Sensor / Manual / Camera / API |

#### Table: Sensor

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| sensor_id | SERIAL | PK | Auto-increment sensor identifier |
| sensor_type | TEXT | — | Inductive Loop / Camera / Radar / CCTV |
| junction_id | INTEGER | FK → Junction NOT NULL | Junction where installed |
| installation_date | DATE | — | Date installed |
| status | TEXT | CHECK IN ('Active','Inactive','Faulty') | Operational status |
| last_reading_time | TIMESTAMP | — | Timestamp of last data received |

---

## 5. Frontend Requirements and Specifications

### 5.1 Architecture

Multi-page Streamlit application. Each page is a separate Python file under `streamlit_app/pages/`. Shared utilities in `api_client.py` (HTTP client, theme injection, table renderer). Role simulation via sidebar dropdown storing role in `st.session_state`. All API calls use `requests` library with `X-User-Role` header. Response caching via `@st.cache_data` (static data: 600s TTL, live data: 60s TTL).

Light theme enforced via CSS injection (`st.markdown(..., unsafe_allow_html=True)`) targeting all Streamlit component `[data-testid]` selectors. All tables rendered as HTML (`df.to_html()`) to avoid Streamlit's internal dark-themed dataframe canvas.

### 5.2 Page Specifications

#### Home (`Home.py`)

**Purpose:** Landing page with live city KPIs and navigation  
**Key Elements:**
- **KPI Strip (4 metrics):** Observations last 24h · Avg Vehicles/Junction · Avg Speed · High Congestion Junctions — loaded from `/api/dashboard`
- **Feature Cards (5 cards):** Clickable cards navigating to each page via `<a href="/Dashboard">` HTML anchors
- **Role badge** in sidebar showing current active role

#### Dashboard (`1_Dashboard.py`)

**Purpose:** City-wide congestion overview with interactive map  
**Key Elements:**
- **Folium Interactive Map:** Centred on Bengaluru (12.972°N, 77.64°E), CartoDB Positron tiles (light)
  - Junction markers: circle markers coloured by congestion level (Red=SEVERE, Orange=HIGH, Blue=MODERATE, Green=LOW, Grey=No data); radius proportional to vehicle count
  - Incident markers: red exclamation-sign icons
  - Click → popup with junction name, zone, congestion, vehicles, speed
- **Junction Status Table** (HTML rendered, light theme)
- **Zone Summary Table**
- **Open Incidents by Severity** (Altair bar chart, white background, branded colours)

#### Traffic Data (`2_Traffic.py`)

**Purpose:** Query and analyse traffic observations  
**Key Elements:**
- Filter bar: Zone, Junction, Congestion Level, Time Window (hours slider)
- Summary metrics: Avg Vehicle Count, Avg Speed, Severe/High count
- Peak-hours bar chart (Altair, blue `#5b7fe8`, white background)
- Observation records table (HTML rendered)

#### Add Observation (`3_Add_Observation.py`)

**Purpose:** Log a new traffic measurement (Officer/Admin only)  
**Key Elements:**
- Zone → Junction cascade dropdowns
- Road dropdown (filtered by zone)
- Vehicle count, avg speed, weather, data source inputs
- Auto-suggested congestion level (client-side logic based on vehicle count)
- POST to `/api/traffic` — demonstrates **ACID Transaction T1 + PostgreSQL trigger**
- Recent observations panel for selected junction

#### Incidents (`4_Incidents.py`)

**Purpose:** Incident management  
**Key Elements:**
- Filters: severity, type, status, zone
- Incident table with resolve/delete actions
- Add incident form (Officer/Admin only)

#### Roads & Zones (`5_Roads_Zones.py`)

**Purpose:** Road network reference + analytics  
**Key Elements:**
- 4 tabs: Roads, Junctions, Zones, Analytics
- Top-5 congested junctions horizontal Altair bar chart
- All tables rendered as HTML (light theme)

### 5.3 Frontend Technical Constraints

- No JavaScript — pure Python/Streamlit
- `@st.cache_data(ttl=600)` for static lookups (zones, roads, junctions)
- `@st.cache_data(ttl=60)` for live data (observations, dashboard, incidents)
- Cache busted (`_get_live.clear()`) after any POST/PUT/DELETE
- `show_table()` helper renders all DataFrames as HTML with `.utms-table` CSS class
- All Altair charts use explicit `background="#ffffff"` in `.properties()` to override Streamlit theme

---

## 6. Backend — API, Connectivity, and Application

### 6.1 Backend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | 0.110+ |
| ASGI Server | Uvicorn | 0.29+ |
| Database | PostgreSQL | 16 |
| DB Connector | psycopg2-binary | 2.9+ |
| Containerisation | Docker + Compose | latest |

### 6.2 REST API Endpoints (20+)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | Any | Health check |
| GET | `/api/zones` | Any | List all zones |
| GET | `/api/roads` | Any | List roads (filter: zone_id, road_type) |
| GET | `/api/junctions` | Any | List junctions (filter: zone_id) |
| GET | `/api/traffic` | Any | List observations (filter: junction_id, congestion_level, hours, limit) |
| POST | `/api/traffic` | officer/admin | Add traffic observation — **ACID Transaction T1** |
| GET | `/api/incidents` | Any | List incidents (filter: severity, status, zone_id) |
| POST | `/api/incidents` | officer/admin | Create new incident |
| PUT | `/api/incidents/{id}` | officer/admin | Update/resolve incident |
| DELETE | `/api/incidents/{id}` | admin only | Delete incident |
| GET | `/api/map` | Any | Map data: junctions with coords + open incidents |
| GET | `/api/dashboard` | Any | KPIs + junction status + zone summary + incident summary |
| GET | `/api/analytics/peak-hours` | Any | Observations grouped by hour-of-day |
| GET | `/api/analytics/zone-summary` | Any | Zone-level aggregates |
| GET | `/api/analytics/top-congested` | Any | Top 5 most congested junctions (last 24h) |

### 6.3 Database Connectivity Pattern

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db():
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", 5432),
        dbname=os.getenv("PGDATABASE", "traffic_db"),
        user=os.getenv("PGUSER", "traffic_user"),
        password=os.getenv("PGPASSWORD", "traffic_pass"),
        cursor_factory=RealDictCursor   # returns rows as dicts
    )
    return conn
```

Key design decisions:
- **`RealDictCursor`**: enables `row['column_name']` access → direct JSON serialization
- Connection created per request; closed in `finally` block
- PostgreSQL MVCC: concurrent readers never blocked by writers (unlike SQLite)
- All queries use `%s` parameterized placeholders — no f-string SQL concatenation

### 6.4 ACID Transaction Demonstration

**Transaction T1: Log Observation + Update Junction Congestion (Atomic)**

```python
conn = get_db()
cur = conn.cursor()
try:
    cur.execute("""
        INSERT INTO Traffic_Observation
            (junction_id, road_id, vehicle_count, avg_speed_kmph,
             congestion_level, weather_condition, data_source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING obs_id
    """, (junction_id, road_id, vehicle_count, avg_speed,
          congestion_level, weather, data_source))
    obs_id = cur.fetchone()['obs_id']
    # PostgreSQL trigger fires automatically on INSERT:
    # trg_update_junction_congestion → updates Junction.congestion_status
    conn.commit()
    return {"obs_id": obs_id}
except psycopg2.IntegrityError as e:
    conn.rollback()
    raise HTTPException(status_code=400, detail=str(e))
finally:
    cur.close()
    conn.close()
```

**ACID Properties demonstrated:**
- **Atomicity**: INSERT + trigger UPDATE are one atomic unit — either both commit or both rollback
- **Consistency**: FK constraints prevent orphan observations; CHECK constraints enforce valid values; trigger maintains `congestion_status` derived attribute
- **Isolation**: PostgreSQL MVCC — concurrent readers see consistent snapshot; `READ COMMITTED` default isolation level
- **Durability**: PostgreSQL WAL ensures committed transactions survive server crash

### 6.5 Triggers and Stored Procedure

#### Trigger: `trg_update_junction_congestion` (AFTER INSERT on Traffic_Observation)
```sql
CREATE OR REPLACE FUNCTION fn_update_junction_congestion()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Junction
    SET congestion_status = NEW.congestion_level
    WHERE junction_id = NEW.junction_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_junction_congestion
AFTER INSERT ON Traffic_Observation
FOR EACH ROW EXECUTE FUNCTION fn_update_junction_congestion();
```

#### Trigger: `trg_incident_audit` (AFTER UPDATE on Incident)
```sql
CREATE OR REPLACE FUNCTION fn_incident_audit()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.severity IS DISTINCT FROM NEW.severity THEN
        INSERT INTO Incident_Audit
            (incident_id, action, old_severity, new_severity, changed_at)
        VALUES (NEW.incident_id, 'UPDATE', OLD.severity, NEW.severity, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_incident_audit
AFTER UPDATE ON Incident
FOR EACH ROW EXECUTE FUNCTION fn_incident_audit();
```

#### Stored Procedure: `sp_resolve_incident`
```sql
CREATE OR REPLACE PROCEDURE sp_resolve_incident(
    p_incident_id INTEGER,
    p_resolved_by TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE Incident
    SET resolved_datetime = NOW(),
        reported_by = p_resolved_by
    WHERE incident_id = p_incident_id
      AND resolved_datetime IS NULL;

    INSERT INTO Incident_Audit(incident_id, action, changed_at, changed_by)
    VALUES (p_incident_id, 'RESOLVED', NOW(), p_resolved_by);
END;
$$;
```

### 6.6 Role-Based Access Control

```
Request → FastAPI route → RBAC dependency → read X-User-Role header
                                           ↓
                               'public' | 'officer' | 'admin'
                                           ↓
     Role hierarchy:  admin > officer > public
     GET endpoints:   any role
     POST/PUT:        officer or admin → 403 if public
     DELETE:          admin only → 403 if officer or public
```

Production PostgreSQL RBAC (SQL):
```sql
CREATE ROLE utms_public;
CREATE ROLE utms_officer;
CREATE ROLE utms_admin;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO utms_public;
GRANT INSERT, UPDATE ON Traffic_Observation, Incident TO utms_officer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO utms_admin;
REVOKE DELETE ON Road, Junction, Zone FROM utms_officer;
```

---

## 7. System Features (DBMS Concepts Demonstrated)

### 7.1 Three-Schema Architecture
External (views) → Conceptual (normalized tables) → Internal (indexes, WAL) — demonstrated live in the running system. See Section 2.1.

### 7.2 ER/EER Modeling
10 entities, 11 relationships, 2 ISA hierarchies (total-disjoint for Vehicle, partial-disjoint for Incident). Full diagram in `docs/ER_Diagram.png`.

### 7.3 ER-to-Relational Mapping
All 7 mapping rules applied in Section 4.3. ISA uses separate table per subtype with shared PK.

### 7.4 Normalization (BCNF)
All 11 base tables verified in BCNF. Full FD analysis and decomposition for Traffic_Observation in Section 4.4.

### 7.5 Indexing
- 7 explicit B-tree indexes on range-query and JOIN columns
- 2 UNIQUE (implicit) indexes on high-cardinality equality columns
- Composite index `idx_obs_junction_time` exploited by `v_junction_live_status` lateral join

### 7.6 ACID Transactions and Concurrency
- Explicit `conn.commit()` / `conn.rollback()` for all multi-step operations
- PostgreSQL MVCC provides snapshot isolation — readers never block writers
- Two-Phase Locking: PostgreSQL acquires row-level locks during UPDATE; released at COMMIT
- No deadlock possible in current schema (single-table UPDATE per transaction)

### 7.7 Recovery (WAL)
- PostgreSQL WAL enabled by default (`wal_level = replica`)
- All writes go to WAL before being applied to heap files
- Crash mid-transaction: PostgreSQL replays WAL to last checkpoint, discards uncommitted changes
- Point-in-time recovery possible via WAL archiving

### 7.8 Security and RBAC
- Application-layer RBAC via `X-User-Role` header in FastAPI dependency
- All SQL parameterized (`%s` placeholders) — SQL injection impossible
- Production GRANT/REVOKE pattern documented in Section 6.6

### 7.9 Query Optimization
- `EXPLAIN ANALYZE` verifies index usage on dashboard query
- Lateral join in `v_junction_live_status` eliminates correlated subquery full scan
- Composite index removes full table scan on Traffic_Observation for time-series lookups

---

## 8. External Interface Requirements

| Interface | Type | Description |
|-----------|------|-------------|
| User Interface | Streamlit (Python) | 6 pages, Folium map, Altair charts |
| Map Tiles | CartoDB Positron (CDN) | Light tile layer via Folium |
| Backend API | REST over HTTP | JSON responses, port 8000 |
| Database | PostgreSQL 16 | Port 5432, psycopg2 connector |
| Container | Docker + Compose | 3 services: postgres, api, streamlit |

### 8.1 Docker Compose Services

```yaml
services:
  postgres:    # PostgreSQL 16, port 5432, pg_data volume
  api:         # FastAPI + Uvicorn, port 8000, depends on postgres
  streamlit:   # Streamlit, port 8501, depends on api
```

**Startup command:**
```bash
docker compose up --build
```

**URLs after startup:**
- Streamlit UI: http://localhost:8501
- FastAPI Swagger docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

---

## 9. Validation and Verification

### 9.1 Manual Verification Test Cases

| Test | Steps | Expected Outcome |
|------|-------|-----------------|
| Trigger fires | Insert observation, SELECT junction congestion_status | junction.congestion_status matches new congestion_level |
| Audit trigger | Update incident severity → SELECT from Incident_Audit | New audit row with old/new severity values |
| ACID rollback | POST /api/traffic with invalid junction_id=9999 | 400 error; no orphan row in Traffic_Observation |
| RBAC enforcement | POST /api/traffic with no role header | 403 Forbidden |
| Stored procedure | CALL sp_resolve_incident(1, 'Admin') | Incident resolved_datetime set; audit row created |
| FK constraint | Attempt INSERT with non-existent zone_id | PostgreSQL FK violation error |
| ISA subtype | INSERT into Vehicle then Vehicle_Car with same vehicle_id | JOIN returns combined attributes |
| Peak hours | GET /api/analytics/peak-hours | ≤ 24 hour buckets, avg_vehicles per hour |

---

## 10. Work-Integrated Activities Mapping

| WIA | Topic | Project Coverage | Deliverable Location |
|-----|-------|-----------------|----------------------|
| **WIA 1** | Conceptual Model — ER/EER Diagram | 10-entity EER diagram with 11 relationships, 2 ISA hierarchies | `docs/ER_Diagram.png` |
| **WIA 2** | Logical Design — Tables in 3NF/BCNF, FDs, Decomposition | All 11 base tables verified BCNF; full FD analysis for Traffic_Observation | Section 4.3 and 4.4; `sql/schema.sql` |
| **WIA 3** | Physical Design — Index Design, B-Tree, Hashing | 7 B-tree indexes + 2 UNIQUE indexes; composite index rationale | Section 4.5; `sql/schema.sql` |
| **WIA 4** | DB Administration — Transactions, Concurrency, Recovery | ACID T1 (INSERT + trigger); PostgreSQL MVCC; WAL recovery | Section 6.4–6.5; `app/main.py` |
| **WIA 5** | Security — Role-Based Access, GRANT/REVOKE | 3-tier RBAC in FastAPI; SQL GRANT/REVOKE for production; audit trigger | Section 6.6; `app/main.py`; `sql/triggers.sql` |

### Syllabus Coverage Summary

| Module | Topic | Coverage |
|--------|-------|----------|
| M1 | DBMS Concepts | Three-schema architecture (§2.1), data independence |
| M2 | ER/EER Modeling | 10 entities, 2 ISA hierarchies (§4.2) |
| M2 | Relational Model | 7-rule ER-to-Relational mapping (§4.3) |
| M3 | SQL | 20+ queries: JOINs, GROUP BY, subqueries, views, triggers (`sql/`) |
| M4 | Normalization | BCNF proof for all 11 tables; FD analysis (§4.4) |
| M5 | Indexing | B-tree indexes; composite index; UNIQUE index rationale (§4.5) |
| M6 | Transactions | ACID demo T1; PostgreSQL MVCC; WAL recovery (§6.4, §7.6, §7.7) |
| M7 | Security | RBAC, GRANT/REVOKE, parameterized SQL (§6.6, §7.8) |
| M8 | Query Optimization | EXPLAIN ANALYZE; lateral join; composite index (§7.9) |

---

## 11. Appendix

### 11.1 Use Case Models

**UC1: Log Traffic Observation**
- Actor: Traffic Officer
- Precondition: Officer role selected; junction and road exist
- Main Flow: Add Observation page → select zone/junction/road → enter vehicle count, speed, congestion → Submit → POST /api/traffic → BEGIN → INSERT Traffic_Observation → Trigger updates Junction.congestion_status → COMMIT → Success message
- Alternate: Invalid junction → FK violation → ROLLBACK → 400 error shown

**UC2: View Congestion Dashboard**
- Actor: Any user
- Flow: Dashboard page → API calls `/api/map` + `/api/dashboard` → Folium renders circle markers → click junction → popup with latest observation data

**UC3: Report Incident**
- Actor: Traffic Officer
- Flow: Incidents page → fill form → POST /api/incidents → row appears in open incidents table → audit INSERT trigger fires

**UC4: Resolve Incident**
- Actor: Traffic Officer / Admin
- Flow: Incidents table → Resolve button → PUT /api/incidents/{id} → CALL sp_resolve_incident() → resolved_datetime set → audit UPDATE trigger fires

**UC5: Analyse Peak Hours**
- Actor: City Planner
- Flow: Traffic Data page → GET /api/analytics/peak-hours → Altair bar chart shows avg vehicle count per hour of day → identify AM/PM peak hours

### 11.2 Viva Preparation — Expected Hard Questions

| # | Question | Answer Summary |
|---|----------|----------------|
| 1 | Why PostgreSQL over SQLite for Term 1? | PostgreSQL supports true MVCC concurrency, stored procedures, LATERAL joins, native TIMESTAMP, and production-grade RBAC via GRANT/REVOKE. SQLite is single-writer; PostgreSQL handles concurrent officers submitting observations simultaneously. |
| 2 | How does MVCC differ from 2PL for concurrency? | 2PL uses locks — readers block writers and vice versa. MVCC gives each transaction a snapshot of the database at its start time; readers never block writers. PostgreSQL uses MVCC by default (READ COMMITTED isolation). |
| 3 | Walk through BCNF decomposition of Traffic_Observation. | obs_id→{junction_id,road_id,...} OK; junction_id→junction_name is transitive (not BCNF). Decompose: remove junction_name, keep junction_id FK. Lossless join on R1∩R2={junction_id} ✓ |
| 4 | How does PostgreSQL WAL recovery work? | WAL writes every change to the WAL log before the heap file. On crash: uncommitted transactions are only in WAL, never flushed to heap. On restart: PostgreSQL replays WAL from last checkpoint, skips uncommitted entries. Committed data is never lost. |
| 5 | Why is the Incident_Audit table not a formal FK to Incident? | Audit logs are immutable historical records. If an Incident is deleted, we still want to keep the audit history. No FK means the audit entry is preserved even if the parent incident is removed. |
| 6 | What does the LATERAL join in v_junction_live_status do? | LATERAL allows the subquery to reference the outer table's junction_id row by row. It fetches the single most recent Traffic_Observation per junction without a correlated subquery full scan — the composite index `idx_obs_junction_time` is used directly. |
| 7 | Explain total vs partial participation in your ISA. | Vehicle: total participation (double line) — every vehicle MUST be exactly one subtype (Car/Truck/Bus/Motorcycle). Incident: partial participation (single line) — an incident may be a generic record with no subtype row if it doesn't fit a specialisation. |

### 11.3 Project File Structure

```
Urban_Traffic_Management_System/
├── app/
│   └── main.py                   # FastAPI backend (20+ endpoints, ACID, RBAC)
├── streamlit_app/
│   ├── Home.py                   # Landing page (KPIs + clickable feature cards)
│   ├── api_client.py             # HTTP client, light theme, show_table(), caching
│   └── pages/
│       ├── 1_Dashboard.py        # Folium map + junction status + incident chart
│       ├── 2_Traffic.py          # Filter observations + peak-hours Altair chart
│       ├── 3_Add_Observation.py  # ACID Transaction T1 demo
│       ├── 4_Incidents.py        # Incident CRUD
│       └── 5_Roads_Zones.py      # Road network + zone analytics
├── sql/
│   ├── schema.sql                # DDL: 13 tables + 8 ISA subtypes + views + indexes
│   └── triggers.sql              # 2 triggers + stored procedure + ACID demo scripts
├── docs/
│   ├── SRS.md                    # This document
│   ├── ER_Diagram.png            # EER diagram export
│   ├── Schema.md                 # Schema narrative
│   └── Term2_Dynamic_Integration.md  # Roadmap for real-world sensor integration
├── tests/
│   └── test_api.py               # pytest test cases
├── docker-compose.yml            # 3 services: postgres, api, streamlit
├── Dockerfile                    # Shared image for api + streamlit
├── init_db.py                    # Schema + seed data initializer
└── requirements.txt              # All Python dependencies
```

### 11.4 Document History

| Version | Date | Description |
|---------|------|-------------|
| 0.1 | Sep 2026 | Initial draft — problem statement and scope |
| 1.0 | Oct 2026 | Complete SRS per IEEE 830 / ISO/IEC/IEEE 29148 |
| 2.0 | Oct 2026 | Updated: 14 API endpoints, Leaflet.js map, WIA mapping, 27 test cases |
| 3.0 | Oct 2026 | **Major revision:** Migrated stack to PostgreSQL 16 + FastAPI + Streamlit; updated all sections to reflect new architecture, endpoints, triggers, stored procedure, Docker Compose, Folium map, Altair charts |

---

*Prepared by: Nimisha Gupta | BITS Pilani WILP | SESAP ZC337 | October 2026*  
*Lab Session 2 Submission — Prototype + SRS | Deadline: 17 October 2026*
