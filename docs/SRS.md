# Software Requirements Specification (SRS)
### Urban Road & Real-Time Traffic Information and Management Database
### BITS Pilani WILP | SESAP ZC337

---

## 1. Problem Statement

> _To be written by Nimisha_

Design and develop a relational database application to manage urban road infrastructure
and real-time traffic information for Bengaluru. The system will enable traffic authorities
to monitor road conditions, log incidents, manage traffic signals, and generate congestion
reports — supporting better traffic planning and faster emergency response.

---

## 2. Scope

- **City in scope:** Bengaluru (can be extended later)
- **Term 1 scope:** Structured relational database — roads, junctions, vehicles, incidents, observations
- **Out of scope (Term 1):** Real-time streaming, GIS/spatial queries, image/video storage

---

## 3. Users of the System

| User | Role | Access Level |
|---|---|---|
| Traffic Police / Control Room | Monitor congestion, log incidents | Read + Write |
| City Planner / Municipal Authority | Generate reports, analyse zones | Read |
| Emergency Services | Find fastest routes, incident lookup | Read |
| Commuters | View congestion, signal status | Read (public) |
| System Admin | Manage users, roles, data integrity | Full Admin |

---

## 4. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | System shall store and manage road and junction data |
| FR2 | System shall record real-time traffic observations at junctions with timestamps |
| FR3 | System shall log and track traffic incidents (accidents, breakdowns, roadblocks) |
| FR4 | System shall manage traffic signal status and timing configurations |
| FR5 | System shall register vehicles and associated driver/owner details |
| FR6 | System shall generate congestion reports by zone and time window |
| FR7 | System shall support incident search by road, junction, date range, and severity |
| FR8 | System shall maintain sensor installation records and health status |
| FR9 | System shall enforce role-based access control for different user types |
| FR10 | System shall enforce referential integrity across all tables |

---

## 5. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR1 | Single-table query response time < 2 seconds |
| NFR2 | System shall support 10,000+ traffic observation records |
| NFR3 | All transactions shall satisfy ACID properties |
| NFR4 | All tables shall be in BCNF (exceptions documented) |
| NFR5 | System shall recover to a consistent state after a simulated crash |
| NFR6 | Index strategy shall be documented and justified for each table |

---

## 6. Entities (Preliminary List)

> Will be refined in ER_Design.md

- ZONE
- ROAD
- JUNCTION
- ROAD_JUNCTION _(bridge table)_
- TRAFFIC_SIGNAL
- VEHICLE
- DRIVER
- INCIDENT
- TRAFFIC_OBSERVATION
- SENSOR

---

## 7. Assumptions

- Data is scoped to Bengaluru city for Term 1
- Real-time data is simulated via batch CSV import (Kaggle dataset)
- SQLite is used as the DBMS per lab specification
- No live API integration in Term 1

---

_Owner: Nimisha | Reviewer: Fasi_
