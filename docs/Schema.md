# Relational Schema + Normalization
### Urban Road & Real-Time Traffic Management System

---

## Status: Pending Phase 2 (ER Design) completion

---

## Relational Schema

> To be filled after ER → Relational mapping is done in Phase 3

---

## Normalization Analysis

> For each table: list FDs, check 1NF → 2NF → 3NF → BCNF

### Template per table

**Table: TRAFFIC_OBSERVATION**

Functional Dependencies:
- obs_id → junction_id, road_id, observation_time, vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source
- _(add more FDs as discovered)_

Normal Form Check:
- 1NF: [ ] All attributes atomic?
- 2NF: [ ] No partial dependencies on composite key?
- 3NF: [ ] No transitive dependencies?
- BCNF: [ ] Every determinant is a candidate key?

Decomposition (if needed):
- _(document any splits made and verify lossless join)_

---

_Owner: Nimisha | Reviewer: Fasi_
