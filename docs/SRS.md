# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## Urban Road & Real-Time Traffic Information and Management Database System

**Document Version:** 1.0  
**Prepared by:** Nimisha Gupta  
**Course:** SESAP ZC337 — Database Systems and Applications  
**Institute:** BITS Pilani, Work Integrated Learning Programmes  
**Date:** October 2026  
**Standard:** IEEE 830-1998 / ISO/IEC/IEEE 29148:2018  

---

## Table of Contents

1. Introduction
2. Overall Description
3. Specific Requirements
4. Database Design
5. Frontend Requirements and Specifications
6. Backend Database Specs, Connectivity and Application
7. System Features
8. External Interface Requirements
9. Validation and Verification
10. Appendix

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the complete requirements for the **Urban Road & Real-Time Traffic Information and Management Database System**, a web-based application backed by a relational database. The system manages Bengaluru's road infrastructure, traffic observations, incident reporting, signal management, and vehicle records. It serves traffic police, city planners, emergency services, and the public through role-differentiated access.

This document is structured per **IEEE 830-1998** and **ISO/IEC/IEEE 29148:2018** and serves as the authoritative reference for developers, evaluators, and the lab examiner.

### 1.2 Scope

**System Name:** Urban Traffic Management System (UTMS)  
**City in Scope:** Bengaluru, Karnataka, India  
**Term 1 Scope:** Fully normalized relational database, REST API backend, simple HTML/JS frontend, CI/CD pipeline with Docker.

The system enables:
- Storage and retrieval of road and junction network data
- Real-time (simulated) traffic observation logging
- Incident registration, tracking, and resolution
- Traffic signal status management
- Vehicle and driver registration
- Congestion analytics by zone, time window, and road segment
- Role-based access control for different user categories

**Out of scope (Term 1):** Live sensor streaming, GIS spatial queries, image/video storage, mobile application.

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
| MVP | Minimum Viable Product |
| CI/CD | Continuous Integration / Continuous Deployment |
| WAL | Write-Ahead Log |

### 1.4 References

- IEEE 830-1998: IEEE Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2018: Systems and Software Engineering — Life Cycle Processes — Requirements Engineering
- Elmasri & Navathe, *Fundamentals of Database Systems*, 7th Edition, Pearson
- Ramez Elmasri & Shamkant B. Navathe, *Database Systems: Models, Languages, Design and Application Programming*, Pearson Education, 5th Edition, 2007
- SQLite Documentation: https://www.sqlite.org/docs.html
- BITS Pilani SESAP ZC337 Lab Assignment Handout, Version 1.0, September 2026

---

## 2. Overall Description

### 2.1 Product Perspective

The Urban Traffic Management System is a three-tier web application:

```
┌─────────────────────────────────┐
│  Presentation Tier (Frontend)   │
│  HTML / CSS / JavaScript        │
│  5 screens: Dashboard, Add Obs, │
│  Search, Incident Mgmt, Roads   │
└────────────────┬────────────────┘
                 │ HTTP REST (JSON)
┌────────────────▼────────────────┐
│  Application Tier (Backend)     │
│  Python Flask REST API          │
│  7+ endpoints, input validation │
│  Parameterized SQL, error hdlg  │
└────────────────┬────────────────┘
                 │ sqlite3 connector
┌────────────────▼────────────────┐
│  Data Tier (Database)           │
│  SQLite (traffic.db)            │
│  10 tables, indexes, triggers   │
│  Views, transactions, security  │
└─────────────────────────────────┘
```

This architecture follows the **Three-Schema Architecture** (ANSI/SPARC):
- **External Schema:** User views via SQL VIEWs (TrafficDashboard, ZoneSummary, IncidentReport)
- **Conceptual Schema:** Normalized relational tables in BCNF
- **Internal Schema:** Physical storage via SQLite (B+ tree indexes, WAL journal)

### 2.2 Product Functions

| Function | Description |
|----------|-------------|
| Road Network Management | Store and query roads, junctions, zones, and their relationships |
| Traffic Observation Logging | Record vehicle count, average speed, congestion level at junctions |
| Incident Management | Log, update, resolve traffic incidents (accidents, breakdowns, roadblocks) |
| Signal Management | Track traffic signal status, timing, and operational health |
| Vehicle & Driver Registry | Maintain vehicle registrations linked to driver/owner details |
| Congestion Analytics | Aggregate reports by zone, time range, road segment |
| Role-Based Access | Enforce Admin / Traffic Officer / Public Read access tiers |
| Data Integrity | Enforce PK/FK constraints, triggers, and NOT NULL rules |

### 2.3 User Characteristics

| User Role | Description | Access Level | Technical Level |
|-----------|-------------|--------------|-----------------|
| System Admin | Manages schema, users, roles, backups | Full DDL + DML | High |
| Traffic Officer / Control Room | Logs incidents and observations | INSERT + UPDATE + SELECT | Medium |
| City Planner / Municipal Authority | Generates reports, analyses congestion | SELECT only | Low–Medium |
| Emergency Services | Queries incidents and fastest-route data | SELECT only | Low |
| Commuter (Public) | Views congestion and signal status | SELECT (public views) | Low |

### 2.4 Constraints

- Database MUST be implemented in **SQLite** (per lab specification)
- All tables MUST be in **BCNF** (with documented justification for any exceptions)
- All referential integrity MUST be enforced through **FOREIGN KEY constraints**
- Backend MUST use **parameterized SQL** — no string concatenation in queries
- Frontend MUST be simple HTML/CSS/JS — no React, no animations, no mobile-specific UI
- CI pipeline MUST trigger on every `git push`
- System MUST demonstrate ACID properties through explicit transaction scenarios

### 2.5 Assumptions and Dependencies

- Data scope is limited to Bengaluru for Term 1
- Real-time sensor data is simulated via batch INSERT from seed data scripts
- SQLite version 3.x with `PRAGMA foreign_keys = ON` enabled
- Python 3.10+ with Flask 2.x
- GitHub repository used for CI/CD via GitHub Actions
- Docker used for containerized deployment

---

## 3. Specific Requirements

### 3.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | The system shall store and manage zone data (zone_id, zone_name, city, area, zone_type) |
| FR2 | The system shall store road data including road type, lane count, speed limit, surface type, and zone association |
| FR3 | The system shall store junction data including GPS coordinates, junction type, and signal control status |
| FR4 | The system shall maintain M:N relationships between roads and junctions via a bridge table |
| FR5 | The system shall store traffic signal configurations including timing and operational status |
| FR6 | The system shall register drivers/owners with license details |
| FR7 | The system shall register vehicles with license plate (unique), type, make, model, and owner linkage |
| FR8 | The system shall support specialisation of vehicles into Car, Truck, Motorcycle, Bus (EER ISA) |
| FR9 | The system shall log traffic observations at junctions with timestamp, vehicle count, average speed, congestion level, weather, and data source |
| FR10 | The system shall log traffic incidents with type, severity, description, timestamps, and links to road/junction/vehicle |
| FR11 | The system shall support specialisation of incidents into Accident, Breakdown, Roadblock, Flooding (EER ISA) |
| FR12 | The system shall maintain sensor installation records and health status at junctions |
| FR13 | The system shall auto-flag junctions as HIGH congestion via trigger when vehicle_count > 200 |
| FR14 | The system shall provide a real-time dashboard view aggregating latest observations per junction |
| FR15 | The system shall support congestion reporting by zone and time window |
| FR16 | The system shall support incident search by road, junction, type, severity, and date range |
| FR17 | The system shall enforce role-based access (Admin, TrafficOfficer, PublicRead) via SQL GRANT/REVOKE |
| FR18 | The system shall support CRUD operations on traffic observations and incidents via REST API |
| FR19 | The system shall return all API responses in JSON format |
| FR20 | The system shall validate all API inputs before executing SQL |
| FR21 | The system shall demonstrate ACID transactions (concurrent observation inserts, incident updates) |
| FR22 | The system shall provide a recovery demonstration via SQLite WAL mode and checkpoint |

### 3.2 Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR1 | Performance | Single-table SELECT queries shall complete in < 2 seconds for up to 10,000 records |
| NFR2 | Performance | Multi-table JOIN queries (≤ 5 tables) shall complete in < 3 seconds for ≤ 1,000 records |
| NFR3 | Security | Only users with Admin role may execute DDL (CREATE, ALTER, DROP) |
| NFR4 | Security | Traffic Officer may INSERT/UPDATE observations and incidents; cannot DROP tables |
| NFR5 | Security | Public Read role may only execute SELECT on approved views |
| NFR6 | Reliability | Database shall enforce NOT NULL and CHECK constraints to prevent corrupt records |
| NFR7 | Reliability | All foreign key constraints shall be active (PRAGMA foreign_keys = ON) |
| NFR8 | Scalability | Schema shall support growth to 100,000 traffic observations and 50,000 vehicles |
| NFR9 | Maintainability | All tables shall be in BCNF; exceptions documented with justification |
| NFR10 | Recoverability | Database shall recover to consistent state after simulated crash using WAL + checkpoint |
| NFR11 | Indexing | B+ tree index shall exist on (junction_id, observation_time) for fast time-series queries |
| NFR12 | Indexing | Index shall exist on license_plate for O(log n) vehicle lookups |
| NFR13 | Portability | Application shall run in Docker container on any Linux/macOS host |
| NFR14 | Traceability | All SQL queries shall use parameterized statements (no raw string interpolation) |

### 3.3 Domain Requirements

- Traffic observation data must comply with BBMP (Bruhat Bengaluru Mahanagara Palike) road network classification
- Incident severity must be one of: LOW, MEDIUM, HIGH, CRITICAL
- Congestion level must be one of: LOW, MODERATE, HIGH, SEVERE
- Vehicle type must be one of: Car, Truck, Motorcycle, Bus, Auto, Other
- Speed limit values must be between 10 and 120 km/h
- Junction coordinates must be valid Bengaluru GPS coordinates (lat: 12.7–13.2, lon: 77.4–77.8)

---

## 4. Database Design

### 4.1 Entity and Attribute Definitions (Conceptual Model)

The conceptual model follows **EER (Enhanced Entity-Relationship)** notation with:
- 10 base entity types
- 2 specialisation hierarchies (ISA)
- 1 M:N relationship resolved via bridge table
- Aggregation on INCIDENT for complex multi-entity relationships

#### Core Entities

| Entity | Key Attributes | Description |
|--------|---------------|-------------|
| ZONE | zone_id (PK) | Administrative city zone (Whitefield, Indiranagar, etc.) |
| ROAD | road_id (PK) | Road segment with type, lanes, speed limit |
| JUNCTION | junction_id (PK) | Intersection/junction with GPS coordinates |
| ROAD_JUNCTION | (road_id, junction_id) PK | Bridge table for M:N Road–Junction |
| TRAFFIC_SIGNAL | signal_id (PK) | Signal at a junction with timing config |
| DRIVER | driver_id (PK) | Vehicle owner/driver with license details |
| VEHICLE | vehicle_id (PK) | Registered vehicle linked to a driver |
| INCIDENT | incident_id (PK) | Traffic event at road/junction involving vehicle |
| TRAFFIC_OBSERVATION | obs_id (PK) | Timestamped traffic measurement at junction |
| SENSOR | sensor_id (PK) | Physical sensor installed at junction |

#### EER Specialisations

```
VEHICLE (total, disjoint ISA)
    ├── Car         (extra attr: num_doors, fuel_type)
    ├── Truck       (extra attr: max_load_tonnes)
    ├── Motorcycle  (extra attr: engine_cc)
    └── Bus         (extra attr: seating_capacity)

INCIDENT (partial, disjoint ISA)
    ├── Accident    (extra attr: injuries_count, fatalities)
    ├── Breakdown   (extra attr: breakdown_cause)
    ├── Roadblock   (extra attr: authority_name)
    └── Flooding    (extra attr: water_level_cm)
```

### 4.2 ER-to-Relational Mapping (All 7 Rules Applied)

**Rule 1 — Regular (Strong) Entity Types:**
Each strong entity becomes a relation. PK preserved.
- Zone(**zone_id**, zone_name, city, area_sqkm, zone_type)
- Road(**road_id**, road_name, road_type, length_km, num_lanes, speed_limit, surface_type, direction_type, zone_id↑Zone)
- Junction(**junction_id**, junction_name, junction_type, latitude, longitude, signal_controlled, zone_id↑Zone)
- Traffic_Signal(**signal_id**, signal_type, installed_date, operational_status, green_duration_sec, junction_id↑Junction)
- Driver(**driver_id**, name, license_no, dob, contact, address)
- Vehicle(**vehicle_id**, license_plate, vehicle_type, make, model, year, registered_state, owner_id↑Driver)
- Sensor(**sensor_id**, sensor_type, installation_date, status, last_reading_time, junction_id↑Junction)

**Rule 2 — Weak Entity Types:** Not applicable (all entities have their own PKs).

**Rule 3 — Binary 1:1 Relationships:** Not applicable.

**Rule 4 — Binary 1:N Relationships:**
FK placed on the N-side.
- Road.zone_id → Zone.zone_id (many roads in one zone)
- Junction.zone_id → Zone.zone_id (many junctions in one zone)
- Traffic_Signal.junction_id → Junction.junction_id
- Vehicle.owner_id → Driver.driver_id
- Sensor.junction_id → Junction.junction_id
- Traffic_Observation.junction_id → Junction.junction_id
- Traffic_Observation.road_id → Road.road_id
- Incident.road_id → Road.road_id (nullable — some incidents at junction only)
- Incident.junction_id → Junction.junction_id (nullable)
- Incident.vehicle_id → Vehicle.vehicle_id (nullable)

**Rule 5 — Binary M:N Relationships:**
New bridge relation with both PKs as composite PK.
- Road_Junction(**road_id**↑Road, **junction_id**↑Junction, position_type)

**Rule 6 — Multivalued Attributes:** Not applicable.

**Rule 7 — N-ary Relationships:** Not applicable.

**ISA Mapping (specialisation — one table per subtype):**
- Car(**vehicle_id**↑Vehicle, num_doors, fuel_type)
- Truck(**vehicle_id**↑Vehicle, max_load_tonnes)
- Motorcycle(**vehicle_id**↑Vehicle, engine_cc)
- Bus(**vehicle_id**↑Vehicle, seating_capacity)
- Accident(**incident_id**↑Incident, injuries_count, fatalities)
- Breakdown(**incident_id**↑Incident, breakdown_cause)
- Roadblock(**incident_id**↑Incident, authority_name)
- Flooding(**incident_id**↑Incident, water_level_cm)

### 4.3 Normalization Analysis

#### TRAFFIC_OBSERVATION Table — Full Normalization Walkthrough

**Unnormalized (before normalization):**
ObsRecord = {obs_id, junction_id, junction_name, zone_id, road_id, road_name, observation_time, vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source}

**Step 1 — First Normal Form (1NF):**
- Condition: All attributes atomic, no repeating groups
- Check: Each cell holds a single value — junction_name is single value, not a list
- Result: Already in 1NF once junction_name and road_name are moved to their own tables

**Step 2 — Second Normal Form (2NF):**
- Condition: No partial dependency on composite key
- PK: obs_id (single attribute) — no composite PK, so 2NF is automatically satisfied
- Result: In 2NF

**Step 3 — Third Normal Form (3NF):**
- Functional Dependencies:
  - obs_id → junction_id, road_id, observation_time, vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source
  - junction_id → junction_name, zone_id (transitive: obs_id → junction_id → junction_name)
  - road_id → road_name (transitive: obs_id → road_id → road_name)
- Transitive dependency detected: obs_id → junction_id → junction_name
- Resolution: Remove junction_name; keep junction_id FK. Junction details in JUNCTION table.
- Result: In 3NF after removal of transitive attributes.

**Step 4 — BCNF:**
- Condition: For every FD X → Y, X must be a candidate key
- After 3NF decomposition, obs_id is the only determinant for all non-key attributes
- No non-trivial FD where LHS is not a superkey
- Result: In BCNF ✓

**Summary of all tables:**

| Table | 1NF | 2NF | 3NF | BCNF | Notes |
|-------|-----|-----|-----|------|-------|
| Zone | ✓ | ✓ | ✓ | ✓ | Single PK, no transitive deps |
| Road | ✓ | ✓ | ✓ | ✓ | zone_id FK, not transitive |
| Junction | ✓ | ✓ | ✓ | ✓ | zone_id FK |
| Road_Junction | ✓ | ✓ | ✓ | ✓ | Composite PK, no non-key attrs except position_type |
| Traffic_Signal | ✓ | ✓ | ✓ | ✓ | junction_id FK |
| Driver | ✓ | ✓ | ✓ | ✓ | license_no is candidate key |
| Vehicle | ✓ | ✓ | ✓ | ✓ | license_plate is candidate key, owner_id FK |
| Incident | ✓ | ✓ | ✓ | ✓ | Nullable FKs for partial participation |
| Traffic_Observation | ✓ | ✓ | ✓ | ✓ | See full analysis above |
| Sensor | ✓ | ✓ | ✓ | ✓ | junction_id FK |

**Lossless Join Property (verified for Traffic_Observation decomposition):**
Original R(obs_id, junction_id, junction_name) decomposed into:
- R1(obs_id, junction_id) and R2(junction_id, junction_name)
- R1 ∩ R2 = {junction_id}; junction_id → junction_name (holds in R2)
- Therefore: lossless join ✓

**Dependency Preserving Property:**
All FDs preserved across decompositions — no FD is lost when splitting tables.

### 4.4 Physical Design — Indexing Strategy

#### B+ Tree Indexes (for range queries and equality on high-cardinality columns)

| Index Name | Table | Column(s) | Justification |
|-----------|-------|-----------|---------------|
| idx_obs_junction_time | Traffic_Observation | (junction_id, observation_time) | Most common query pattern: find recent observations for a junction — composite index enables index-only scan |
| idx_obs_road | Traffic_Observation | road_id | Queries filtering by road segment |
| idx_incident_road | Incident | road_id | Incident search by road |
| idx_incident_junction | Incident | junction_id | Incident search by junction |
| idx_incident_datetime | Incident | reported_datetime | Date-range incident queries |
| idx_road_zone | Road | zone_id | Zone-based road queries |
| idx_junction_zone | Junction | zone_id | Zone-based junction queries |

#### Hash-Equivalent Index (for exact equality lookups)

| Index Name | Table | Column | Justification |
|-----------|-------|--------|---------------|
| idx_vehicle_plate | Vehicle | license_plate | UNIQUE constraint creates an implicit index — O(1) lookup by plate number. Equivalent to static external hashing for exact match. |
| idx_driver_license | Driver | license_no | UNIQUE license number lookup |

#### B+ Tree vs Hash — Design Rationale

- **B+ Tree** chosen for observation_time, junction_id: supports range queries (WHERE observation_time BETWEEN ...) and ORDER BY efficiently. Leaf nodes form a linked list enabling sequential access without full scan.
- **Hash** (via UNIQUE index) chosen for license_plate: only equality lookups needed (no range scan). O(1) average lookup vs O(log n) for B+ tree. No ordering required.
- B+ tree preferred over B-tree because: leaf nodes store all actual data records (or pointers); internal nodes store only keys; supports sequential scans without traversing entire tree.

### 4.5 Data Dictionary

#### Table: Zone

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| zone_id | INTEGER | PK, NOT NULL | Unique zone identifier |
| zone_name | TEXT | NOT NULL | Name (e.g., "Whitefield", "Indiranagar") |
| city | TEXT | NOT NULL, DEFAULT 'Bengaluru' | City name |
| area_sqkm | REAL | CHECK > 0 | Zone area in square kilometers |
| zone_type | TEXT | CHECK IN (...) | Residential/Commercial/Industrial/Mixed |

#### Table: Road

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| road_id | INTEGER | PK, NOT NULL | Unique road identifier |
| road_name | TEXT | NOT NULL | Full road name |
| road_type | TEXT | CHECK IN (...) | National Highway/State Highway/City Road/Lane |
| length_km | REAL | CHECK > 0 | Road segment length |
| num_lanes | INTEGER | CHECK > 0 | Number of lanes |
| speed_limit | INTEGER | CHECK BETWEEN 10 AND 120 | Speed limit in km/h |
| surface_type | TEXT | — | Asphalt/Concrete/Gravel |
| direction_type | TEXT | — | One-way/Two-way/Divided |
| zone_id | INTEGER | FK → Zone, NOT NULL | Zone this road belongs to |

#### Table: Junction

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| junction_id | INTEGER | PK, NOT NULL | Unique junction identifier |
| junction_name | TEXT | NOT NULL | Name (e.g., "Silk Board Junction") |
| junction_type | TEXT | CHECK IN (...) | Signalised/Unsignalised/Roundabout/Flyover |
| latitude | REAL | CHECK BETWEEN 12.7 AND 13.2 | Bengaluru latitude range |
| longitude | REAL | CHECK BETWEEN 77.4 AND 77.8 | Bengaluru longitude range |
| signal_controlled | INTEGER | DEFAULT 0 | 0=No, 1=Yes (Boolean) |
| congestion_status | TEXT | DEFAULT 'NORMAL' | NORMAL/HIGH — updated by trigger |
| zone_id | INTEGER | FK → Zone, NOT NULL | Zone this junction belongs to |

#### Table: Road_Junction

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| road_id | INTEGER | PK (composite), FK → Road | Road in the junction |
| junction_id | INTEGER | PK (composite), FK → Junction | Junction on the road |
| position_type | TEXT | — | Start/End/Intermediate |

#### Table: Traffic_Signal

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| signal_id | INTEGER | PK, NOT NULL | Unique signal identifier |
| junction_id | INTEGER | FK → Junction, NOT NULL | Junction where signal is installed |
| signal_type | TEXT | — | Standard/Adaptive/Pedestrian |
| installed_date | DATE | — | Installation date |
| operational_status | TEXT | CHECK IN (...) | Active/Inactive/Faulty/Under Maintenance |
| green_duration_sec | INTEGER | CHECK > 0 | Green phase duration in seconds |

#### Table: Driver

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| driver_id | INTEGER | PK, NOT NULL | Unique driver identifier |
| name | TEXT | NOT NULL | Full name |
| license_no | TEXT | UNIQUE, NOT NULL | Driving license number |
| dob | DATE | — | Date of birth |
| contact | TEXT | — | Phone number |
| address | TEXT | — | Residential address |

#### Table: Vehicle

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| vehicle_id | INTEGER | PK, NOT NULL | Unique vehicle identifier |
| license_plate | TEXT | UNIQUE, NOT NULL | Registration number (e.g., KA-01-AB-1234) |
| vehicle_type | TEXT | CHECK IN (...) | Car/Truck/Motorcycle/Bus/Auto/Other |
| make | TEXT | — | Manufacturer (Maruti, Tata, etc.) |
| model | TEXT | — | Model name |
| year | INTEGER | CHECK BETWEEN 1990 AND 2030 | Manufacturing year |
| registered_state | TEXT | — | State of registration |
| owner_id | INTEGER | FK → Driver | Owner/driver reference |

#### Table: Incident

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| incident_id | INTEGER | PK, NOT NULL | Unique incident identifier |
| incident_type | TEXT | NOT NULL, CHECK IN (...) | Accident/Breakdown/Roadblock/Flooding |
| severity | TEXT | CHECK IN (...) | LOW/MEDIUM/HIGH/CRITICAL |
| description | TEXT | — | Free-text description |
| reported_datetime | DATETIME | NOT NULL | Timestamp when incident reported |
| resolved_datetime | DATETIME | — | Timestamp when incident resolved (NULL if open) |
| road_id | INTEGER | FK → Road | Road where incident occurred |
| junction_id | INTEGER | FK → Junction | Junction (nullable) |
| vehicle_id | INTEGER | FK → Vehicle | Vehicle involved (nullable) |
| reported_by | TEXT | — | Name/role of reporting party |

#### Table: Traffic_Observation

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| obs_id | INTEGER | PK, NOT NULL | Unique observation identifier |
| junction_id | INTEGER | FK → Junction, NOT NULL | Junction observed |
| road_id | INTEGER | FK → Road, NOT NULL | Road segment observed |
| observation_time | DATETIME | NOT NULL | ISO 8601 timestamp |
| vehicle_count | INTEGER | CHECK >= 0 | Total vehicles counted |
| avg_speed_kmph | REAL | CHECK >= 0 | Average speed in km/h |
| congestion_level | TEXT | CHECK IN (...) | LOW/MODERATE/HIGH/SEVERE |
| weather_condition | TEXT | — | Clear/Rainy/Foggy/Cloudy |
| data_source | TEXT | — | Sensor/Manual/Camera |

#### Table: Sensor

| Column | Data Type | Constraint | Description |
|--------|-----------|-----------|-------------|
| sensor_id | INTEGER | PK, NOT NULL | Unique sensor identifier |
| sensor_type | TEXT | — | Inductive Loop/Camera/Radar/CCTV |
| junction_id | INTEGER | FK → Junction, NOT NULL | Junction where installed |
| installation_date | DATE | — | Date installed |
| status | TEXT | CHECK IN (...) | Active/Inactive/Faulty |
| last_reading_time | DATETIME | — | Timestamp of last data received |

---

## 5. Frontend Requirements and Specifications

### 5.1 Architecture

Simple HTML/CSS/JavaScript single-page applications. No frameworks. Vanilla JS with `fetch()` for REST API calls. Consistent header/navigation across all screens.

### 5.2 Screen Specifications

#### Screen 1: Dashboard (`/` or `index.html`)
**Purpose:** Overview of current traffic conditions  
**Elements:**
- Summary cards: Total Active Incidents, Junctions with HIGH Congestion, Observations Today
- Junction selector dropdown → shows latest observation for selected junction
- Top 5 Most Congested Junctions (table: junction name, congestion level, vehicle count, time)
- Recent Incidents (table: type, severity, road, reported time)

#### Screen 2: Add Traffic Observation (`/add_observation.html`)
**Purpose:** Log a new traffic measurement  
**Elements:**
- Form: Junction (dropdown), Road (dropdown), Vehicle Count (number), Avg Speed (number), Congestion Level (select), Weather (select), Data Source (select), Timestamp (datetime-local)
- Submit button → POST /api/traffic
- Success/error message display

#### Screen 3: Search / View Traffic Data (`/search_traffic.html`)
**Purpose:** Query and analyse traffic observations  
**Elements:**
- Filter form: Junction (dropdown), Road (dropdown), Date From, Date To, Congestion Level (select)
- Results table with pagination (20 rows)
- Summary stats: average speed, peak vehicle count for filtered period

#### Screen 4: Incident Management (`/incidents.html`)
**Purpose:** Log, view, update, and close incidents  
**Elements:**
- Add Incident form: type, severity, description, road, junction, vehicle plate (optional), reported by
- Incidents table: shows all open incidents with Edit and Resolve buttons
- Edit triggers PUT /api/incident/{id}
- Resolve button sets resolved_datetime

#### Screen 5: Roads & Junctions (`/roads_junctions.html`)
**Purpose:** Reference data browser  
**Elements:**
- Zone filter → shows roads and junctions in that zone
- Roads table: name, type, lanes, speed limit, zone
- Junctions table: name, type, coordinates, signal controlled

### 5.3 Frontend Technical Constraints

- No CSS framework (Bootstrap allowed for grid only if simple; plain CSS preferred)
- No JavaScript framework (vanilla JS only)
- All API calls via `fetch()` with JSON
- Form validation in JS before submission
- Error messages displayed inline (no alert() popups)

---

## 6. Backend Database Specs, Connectivity and Application

### 6.1 Backend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| Web Framework | Flask | 2.3+ |
| Database | SQLite | 3.x |
| DB Connector | sqlite3 (stdlib) | — |
| WSGI Server | Gunicorn (production) | 21.x |

### 6.2 REST API Endpoints

| Method | Endpoint | Description | SQL Operation |
|--------|----------|-------------|---------------|
| GET | /api/roads | List all roads (with zone name) | SELECT + JOIN |
| GET | /api/junctions | List all junctions | SELECT |
| GET | /api/traffic | List observations (filterable) | SELECT + JOIN + WHERE |
| GET | /api/traffic/road/<road_id> | Observations for a specific road | SELECT + WHERE |
| GET | /api/incidents | List incidents (open/all) | SELECT + JOIN |
| GET | /api/dashboard | Dashboard summary stats | Multiple SELECTs |
| POST | /api/traffic | Add traffic observation | INSERT (parameterized) |
| POST | /api/incident | Add new incident | INSERT (parameterized) |
| PUT | /api/incident/<id> | Update incident | UPDATE (parameterized) |
| DELETE | /api/incident/<id> | Delete incident | DELETE |

### 6.3 Database Connectivity

```python
# Standard connection pattern
import sqlite3

DB_PATH = 'data/traffic.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # enables dict-style access
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Log for concurrency
    return conn
```

### 6.4 Input Validation Rules

| Field | Validation |
|-------|-----------|
| junction_id / road_id | Must be INTEGER, must exist in DB (FK check) |
| vehicle_count | INTEGER, must be >= 0 |
| avg_speed_kmph | REAL, must be >= 0 |
| congestion_level | Must be in {LOW, MODERATE, HIGH, SEVERE} |
| incident_type | Must be in {Accident, Breakdown, Roadblock, Flooding} |
| severity | Must be in {LOW, MEDIUM, HIGH, CRITICAL} |
| observation_time | Must be valid ISO 8601 datetime |

### 6.5 Transaction Demonstration (ACID Properties)

**Scenario: Concurrent Incident Update + Observation Insert**

```sql
-- Transaction T1: Log observation AND update junction congestion (atomic)
BEGIN TRANSACTION;
    INSERT INTO Traffic_Observation(junction_id, road_id, observation_time, vehicle_count, ...)
    VALUES (?, ?, datetime('now'), ?, ...);
    
    UPDATE Junction SET congestion_status = 'HIGH'
    WHERE junction_id = ? AND ? > 200;
COMMIT;

-- If any step fails: ROLLBACK ensures atomicity
-- ISOLATION: SQLite WAL mode allows concurrent reads during write
-- DURABILITY: WAL journal ensures committed data survives crash
-- CONSISTENCY: FK constraints prevent orphan observations
```

### 6.6 Security Implementation

```sql
-- Role definitions and access control
-- (Demonstrated in SQLite context via application-layer role checks)

-- Admin role: full access
-- SQL pattern: no restriction

-- Traffic Officer role: INSERT/UPDATE on observations and incidents
-- Application enforces: cannot call DELETE on roads/junctions

-- Public role: SELECT only via views
CREATE VIEW PublicTrafficView AS
    SELECT j.junction_name, t.observation_time, t.congestion_level, t.vehicle_count
    FROM Traffic_Observation t
    JOIN Junction j ON t.junction_id = j.junction_id
    WHERE t.observation_time >= datetime('now', '-1 hour');

-- In a production RDBMS (PostgreSQL):
-- GRANT SELECT ON PublicTrafficView TO public_role;
-- GRANT INSERT ON Traffic_Observation TO officer_role;
-- REVOKE DELETE ON Traffic_Observation FROM officer_role;
```

---

## 7. System Features

### 7.1 Data Integrity

- PK/FK constraints enforced with `PRAGMA foreign_keys = ON`
- CHECK constraints on all enumerated and range-bounded fields
- NOT NULL on all critical identifying attributes
- UNIQUE constraints on license_plate, license_no
- Cascading delete behaviour documented per relationship

### 7.2 Normalization (BCNF Compliance)

All 10 tables verified in BCNF. Normalization walkthrough for Traffic_Observation documented in Section 4.3. No anomalous update/insert/delete situations exist in the current schema.

### 7.3 Indexing (Physical Design)

B+ tree indexes on high-frequency JOIN and WHERE columns. Hash-equivalent UNIQUE indexes for exact-match lookups. See Section 4.4 for full index strategy with justification.

### 7.4 Transactions and Concurrency

- WAL journal mode enables concurrent readers during write transactions
- Explicit BEGIN/COMMIT wrappers on all multi-step operations
- Two-phase locking (2PL) demonstrated: Lock acquired on Junction before UPDATE; lock released after COMMIT — prevents lost update anomaly in concurrent signal updates
- Deadlock prevention: consistent lock ordering (always lock Junction before Observation)

### 7.5 Recovery

- SQLite WAL (Write-Ahead Log) mode: all changes written to WAL file before applied to DB
- Checkpoint operation: WAL merged back to main DB file
- Crash recovery: on restart, SQLite replays committed WAL entries, discards uncommitted
- Demonstration script: simulate crash mid-transaction, verify recovery to consistent state

### 7.6 Query Optimization

- EXPLAIN QUERY PLAN used to verify index utilisation on key queries
- Composite index on (junction_id, observation_time) avoids full table scan for dashboard query
- View TrafficDashboard uses correlated subquery; optimized with index on observation_time

---

## 8. External Interface Requirements

| Interface | Type | Description |
|-----------|------|-------------|
| User Interface | HTML/CSS/JS in browser | 5 screens, vanilla JS fetch() |
| Backend API | REST over HTTP | JSON responses, localhost:5000 |
| Database | SQLite file | data/traffic.db, sqlite3 library |
| CI/CD | GitHub Actions | .github/workflows/ci.yml |
| Container | Docker | Dockerfile + docker-compose.yml |

---

## 9. Validation and Verification

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| T1 | Insert observation with valid junction_id | Record inserted, 201 returned |
| T2 | Insert observation with invalid junction_id | FK violation, 400 returned |
| T3 | Insert vehicle_count = 250 | Trigger fires, junction congestion_status set to HIGH |
| T4 | Query top 5 congested junctions | Returns 5 rows ordered by avg congestion DESC |
| T5 | Delete incident with valid id | Record deleted, 200 returned |
| T6 | Delete incident with invalid id | 404 returned |
| T7 | Concurrent INSERT and UPDATE in transaction | Both succeed or both rollback (atomicity) |
| T8 | Simulate crash mid-transaction | DB recovers to last committed state via WAL |
| T9 | EXPLAIN on dashboard query | Shows index usage on idx_obs_junction_time |
| T10 | 4-table JOIN (Junction–Observation–Road–Zone) | Executes < 3 seconds for 1,000 records |
| T11 | Role check: public role trying DELETE | Rejected at application layer |
| T12 | Normalization check: Traffic_Observation | No transitive dependencies found |

---

## 10. Appendix

### 10.1 Use Case Models

**UC1: Log Traffic Observation**
- Actor: Traffic Officer
- Precondition: Officer logged in, junction and road selected
- Flow: Select junction → enter vehicle count, speed, congestion → submit → system inserts record → trigger checks if HIGH congestion → success message
- Alternate: Invalid data → validation error shown inline

**UC2: View Congestion Dashboard**
- Actor: Any user (Public)
- Flow: Load dashboard → system queries TrafficDashboard view → display junction summary cards → user selects junction → system returns latest observation
- Result: Real-time-like view of traffic conditions

**UC3: Report Incident**
- Actor: Traffic Officer
- Flow: Navigate to Incidents → fill form → submit → POST /api/incident → record created → appears in open incidents table

**UC4: Resolve Incident**
- Actor: Traffic Officer / Admin
- Flow: View open incidents → click Resolve → PUT /api/incident/{id} with resolved_datetime = now → incident marked resolved

**UC5: Search Traffic History**
- Actor: City Planner
- Flow: Set date range + zone filter → GET /api/traffic with query params → results table → analyse congestion trends

### 10.2 Future Enhancements (Term 2)

- PostGIS spatial data: junction coordinates as geometry type, ST_Distance queries
- R-Tree spatial indexing for road-network proximity queries
- TimescaleDB for partitioned time-series sensor data
- Traffic camera image storage (file path + BLOB thumbnail)
- Incident heatmap visualization via Folium/Leaflet.js
- Real-time sensor data ingestion via WebSocket

### 10.3 Document History

| Version | Date | Description |
|---------|------|-------------|
| 0.1 | Sep 2026 | Initial draft — problem statement and scope |
| 1.0 | Oct 2026 | Complete SRS per IEEE 830 / ISO/IEC/IEEE 29148 |

---

*Prepared by: Nimisha Gupta | BITS Pilani WILP | SESAP ZC337 | October 2026*
