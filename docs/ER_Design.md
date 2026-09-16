# ER / EER Design Document
### Urban Road & Real-Time Traffic Management System

---

## Status: [ ] Not Started | [ ] In Progress | [x] Pending Phase 1 completion

---

## Entities & Attributes

> To be filled in Phase 2 after SRS is finalised

### ZONE
| Attribute | Type | Constraint |
|---|---|---|
| zone_id | INT | PK |
| zone_name | VARCHAR | NOT NULL |
| city | VARCHAR | NOT NULL |
| area_sqkm | DECIMAL | — |
| zone_type | VARCHAR | — |

### ROAD
| Attribute | Type | Constraint |
|---|---|---|
| road_id | INT | PK |
| road_name | VARCHAR | NOT NULL |
| road_type | VARCHAR | — |
| length_km | DECIMAL | — |
| num_lanes | INT | — |
| speed_limit | INT | — |
| surface_type | VARCHAR | — |
| direction_type | VARCHAR | — |
| zone_id | INT | FK → ZONE |

### JUNCTION
| Attribute | Type | Constraint |
|---|---|---|
| junction_id | INT | PK |
| junction_name | VARCHAR | NOT NULL |
| junction_type | VARCHAR | — |
| latitude | DECIMAL | — |
| longitude | DECIMAL | — |
| signal_controlled | BOOLEAN | — |
| zone_id | INT | FK → ZONE |

### TRAFFIC_SIGNAL
| Attribute | Type | Constraint |
|---|---|---|
| signal_id | INT | PK |
| junction_id | INT | FK → JUNCTION |
| signal_type | VARCHAR | — |
| installed_date | DATE | — |
| operational_status | VARCHAR | — |
| green_duration_sec | INT | — |

### VEHICLE
| Attribute | Type | Constraint |
|---|---|---|
| vehicle_id | INT | PK |
| license_plate | VARCHAR | UNIQUE, NOT NULL |
| vehicle_type | VARCHAR | — |
| make | VARCHAR | — |
| model | VARCHAR | — |
| year | INT | — |
| registered_state | VARCHAR | — |
| owner_id | INT | FK → DRIVER |

### DRIVER
| Attribute | Type | Constraint |
|---|---|---|
| driver_id | INT | PK |
| name | VARCHAR | NOT NULL |
| license_no | VARCHAR | UNIQUE |
| dob | DATE | — |
| contact | VARCHAR | — |
| address | TEXT | — |

### INCIDENT
| Attribute | Type | Constraint |
|---|---|---|
| incident_id | INT | PK |
| incident_type | VARCHAR | NOT NULL |
| severity | VARCHAR | — |
| description | TEXT | — |
| reported_datetime | DATETIME | NOT NULL |
| resolved_datetime | DATETIME | — |
| road_id | INT | FK → ROAD |
| junction_id | INT | FK → JUNCTION (nullable) |
| vehicle_id | INT | FK → VEHICLE (nullable) |
| reported_by | VARCHAR | — |

### TRAFFIC_OBSERVATION
| Attribute | Type | Constraint |
|---|---|---|
| obs_id | INT | PK |
| junction_id | INT | FK → JUNCTION |
| road_id | INT | FK → ROAD |
| observation_time | DATETIME | NOT NULL |
| vehicle_count | INT | — |
| avg_speed_kmph | DECIMAL | — |
| congestion_level | VARCHAR | — |
| weather_condition | VARCHAR | — |
| data_source | VARCHAR | — |

### SENSOR
| Attribute | Type | Constraint |
|---|---|---|
| sensor_id | INT | PK |
| sensor_type | VARCHAR | — |
| junction_id | INT | FK → JUNCTION |
| installation_date | DATE | — |
| status | VARCHAR | — |
| last_reading_time | DATETIME | — |

---

## Relationships

| Relationship | Entities | Cardinality | Notes |
|---|---|---|---|
| belongs_to | ROAD — ZONE | M:1 | Many roads in one zone |
| belongs_to | JUNCTION — ZONE | M:1 | Many junctions in one zone |
| connects | ROAD — JUNCTION | M:N | Via ROAD_JUNCTION bridge |
| has | JUNCTION — TRAFFIC_SIGNAL | 1:M | One junction, many signals |
| owns | DRIVER — VEHICLE | 1:M | One driver owns many vehicles |
| involves | INCIDENT — ROAD | M:1 | — |
| occurs_at | INCIDENT — JUNCTION | M:1 | Nullable |
| involves | INCIDENT — VEHICLE | M:1 | Nullable |
| recorded_at | TRAFFIC_OBSERVATION — JUNCTION | M:1 | — |
| on | TRAFFIC_OBSERVATION — ROAD | M:1 | — |
| installed_at | SENSOR — JUNCTION | M:1 | — |

---

## EER Extensions (Specialisation)

- VEHICLE → {Car, Truck, Motorcycle, Bus} *(total, disjoint)*
- INCIDENT → {Accident, Breakdown, Roadblock, Flooding} *(partial, disjoint)*

---

## ER Diagram

> `ER_Diagram.png` — to be exported from draw.io

---

_Owner: Nimisha | Reviewer: Fasi_
