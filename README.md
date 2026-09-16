# Urban Road & Real-Time Traffic Information and Management Database
### BITS Pilani WILP | SESAP ZC337 — Database Systems and Applications
### Team: Nimisha (I578445) · Fasi Ahmed Khan (I578459)

---

## Project Overview

A two-term capstone project to design, develop, and demonstrate a database application
for managing roads, junctions, traffic conditions, incidents, vehicles, and real-time
traffic observations for an urban area (Bengaluru).

- **Term 1:** Structured/Text relational database (SRS → ER/EER → Schema → SQL → Prototype)
- **Term 2:** Multimodal extension (GIS/spatial data, traffic images, sensor time-series)

---

## Folder Structure

```
Urban_Traffic_Management_System/
├── README.md
├── docs/
│   ├── SRS.md                  ← Phase 1: Requirements
│   ├── ER_Design.md            ← Phase 2: Entity & relationship decisions
│   ├── ER_Diagram.png          ← Phase 2: draw.io export
│   ├── Schema.md               ← Phase 3: Relational schema + normalization
│   └── Multimodal_Plan.md      ← Term 2 planning
├── sql/
│   ├── schema.sql              ← CREATE TABLE statements
│   ├── queries.sql             ← SELECT queries (simple → complex)
│   └── triggers.sql            ← Triggers, views, stored procedures
└── app/
    └── main.py                 ← Python/Streamlit prototype
```

---

## Team Responsibilities

| Area | Nimisha | Fasi |
|---|---|---|
| SRS Document | owns | reviews |
| ER / EER Diagram | owns | contributes |
| Normalization (FDs, BCNF) | owns | reviews |
| SQLite Schema Creation | — | owns |
| Data Sourcing & Import | — | owns |
| SQL Queries | shared | shared |
| Triggers / Views | owns | — |
| Application Prototype | — | owns |
| Transactions + Concurrency | owns | — |
| Security (roles, GRANT) | owns | — |
| Recovery Demo | shared | shared |

---

## Tech Stack

- **Database:** SQLite + SQLiteBrowser
- **Language:** Python / SQL
- **Modelling:** draw.io (ER diagrams)
- **UI:** Streamlit
- **Version Control:** GitHub (SAP internal)

---

## Key Dates

| Date | Milestone |
|---|---|
| Sep 16–20 | Phase 1: SRS complete |
| Sep 21–30 | Phase 2: ER/EER Diagram |
| ~Oct 01 | **Mid-Semester Exam — freeze project 3 days before** |
| Oct 06–14 | Phase 3: Schema + Normalization |
| Oct 15–26 | Phase 4: SQL Implementation |
| Oct 27–Nov 09 | Phase 5: Application Prototype |
| Nov 10–16 | Phase 6: Term 1 wrap-up |
| Nov 17–30 | Phase 7: Term 2 Multimodal Planning |
