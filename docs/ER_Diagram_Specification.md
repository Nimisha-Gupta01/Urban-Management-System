# ER / EER Diagram — Complete Specification
## Urban Road & Real-Time Traffic Management System
### BITS Pilani WILP | SESAP ZC337

---

## How to use this document

This file gives you **everything** needed to draw the ER diagram manually (draw.io, Lucidchart, or pen-and-paper) **or** to paste into an AI image generator.  
At the bottom is a ready-to-paste prompt for ChatGPT / Gemini / any AI image tool.

---

## Section 1 — Drawing Rules (Standard ER Notation)

| Shape | What it represents |
|-------|--------------------|
| **Rectangle** | Entity (strong entity) |
| **Double Rectangle** | Weak entity (none in this diagram) |
| **Ellipse / Oval** | Attribute |
| **Double Ellipse** | Multi-valued attribute (none here) |
| **Dashed Ellipse** | Derived attribute (none here) |
| **Underlined text in ellipse** | Primary Key attribute |
| **Diamond** | Relationship |
| **Double Diamond** | Identifying relationship for weak entity (none here) |
| **Line** | Connects entity to its attributes and to relationships |
| **1 and M / N labels on lines** | Cardinality (1:N, M:N, 1:1) |
| **Single line** | Partial participation |
| **Double line** | Total participation |
| **Triangle with "ISA"** | Specialisation / Generalisation (EER) |
| **d inside ISA triangle** | Disjoint specialisation |
| **o inside ISA triangle** | Overlapping specialisation |

---

## Section 2 — All Entities with Their Attributes

Draw each entity as a **rectangle** with its name in bold inside.  
Draw each attribute as an **ellipse** connected by a line to the entity.  
**Underline** the primary key attribute.

---

### ENTITY 1: ZONE
**Rectangle label:** `ZONE`

Attributes (ellipses connected to ZONE):
- `zone_id` — **underlined** (Primary Key)
- `zone_name`
- `city`
- `area_sqkm`
- `zone_type`

---

### ENTITY 2: ROAD
**Rectangle label:** `ROAD`

Attributes:
- `road_id` — **underlined** (PK)
- `road_name`
- `road_type`
- `length_km`
- `num_lanes`
- `speed_limit`
- `surface_type`
- `direction_type`
- `zone_id` ← this is a Foreign Key; **do not draw as ellipse** — it is shown via the relationship line to ZONE

---

### ENTITY 3: JUNCTION
**Rectangle label:** `JUNCTION`

Attributes:
- `junction_id` — **underlined** (PK)
- `junction_name`
- `junction_type`
- `latitude`
- `longitude`
- `signal_controlled`
- `congestion_status`
- `zone_id` ← shown via relationship line to ZONE

---

### ENTITY 4: ROAD_JUNCTION  *(Bridge / Associative Entity)*
**Rectangle label:** `ROAD_JUNCTION`

> This is the bridge table for the M:N relationship between ROAD and JUNCTION.  
> Draw it as a rectangle inside or touching the relationship diamond, **or** draw it as a separate rectangle connected to both ROAD and JUNCTION.

Attributes:
- `road_id` — **underlined** (part of composite PK, FK → ROAD)
- `junction_id` — **underlined** (part of composite PK, FK → JUNCTION)
- `position_type`

---

### ENTITY 5: TRAFFIC_SIGNAL
**Rectangle label:** `TRAFFIC_SIGNAL`

Attributes:
- `signal_id` — **underlined** (PK)
- `signal_type`
- `installed_date`
- `operational_status`
- `green_duration_sec`
- `junction_id` ← shown via relationship line to JUNCTION

---

### ENTITY 6: DRIVER
**Rectangle label:** `DRIVER`

Attributes:
- `driver_id` — **underlined** (PK)
- `name`
- `license_no` ← also a candidate key (unique) — can draw with dashed underline
- `dob`
- `contact`
- `address`

---

### ENTITY 7: VEHICLE
**Rectangle label:** `VEHICLE`

Attributes:
- `vehicle_id` — **underlined** (PK)
- `license_plate` ← candidate key — dashed underline
- `vehicle_type`
- `make`
- `model`
- `year`
- `registered_state`
- `owner_id` ← shown via relationship line to DRIVER

---

### ENTITY 8: INCIDENT
**Rectangle label:** `INCIDENT`

Attributes:
- `incident_id` — **underlined** (PK)
- `incident_type`
- `severity`
- `description`
- `reported_datetime`
- `resolved_datetime`
- `reported_by`
- `road_id` ← shown via relationship line to ROAD
- `junction_id` ← shown via relationship line to JUNCTION
- `vehicle_id` ← shown via relationship line to VEHICLE

---

### ENTITY 9: TRAFFIC_OBSERVATION
**Rectangle label:** `TRAFFIC_OBSERVATION`

Attributes:
- `obs_id` — **underlined** (PK)
- `observation_time`
- `vehicle_count`
- `avg_speed_kmph`
- `congestion_level`
- `weather_condition`
- `data_source`
- `junction_id` ← shown via relationship line to JUNCTION
- `road_id` ← shown via relationship line to ROAD

---

### ENTITY 10: SENSOR
**Rectangle label:** `SENSOR`

Attributes:
- `sensor_id` — **underlined** (PK)
- `sensor_type`
- `installation_date`
- `status`
- `last_reading_time`
- `junction_id` ← shown via relationship line to JUNCTION

---

## Section 3 — All Relationships (Draw as Diamonds)

Each relationship is a **diamond** shape placed between the two entities it connects.  
Label the diamond with the relationship name.  
Write cardinality (1, M, N) on each line near the entity.

---

| # | Relationship Name | Entity 1 | Cardinality | Entity 2 | Participation |
|---|-------------------|----------|-------------|----------|---------------|
| R1 | **BELONGS_TO** | ROAD | M | ZONE | 1 | Road: total (double line); Zone: partial |
| R2 | **LOCATED_IN** | JUNCTION | M | ZONE | 1 | Junction: total; Zone: partial |
| R3 | **CONNECTS** | ROAD | M | JUNCTION | N | Both partial — resolved via ROAD_JUNCTION bridge |
| R4 | **HAS_SIGNAL** | JUNCTION | 1 | TRAFFIC_SIGNAL | M | Signal: total (must belong to a junction) |
| R5 | **OWNS** | DRIVER | 1 | VEHICLE | M | Vehicle: partial (owner can be null) |
| R6 | **OBSERVED_AT** | TRAFFIC_OBSERVATION | M | JUNCTION | 1 | Observation: total |
| R7 | **RECORDED_ON** | TRAFFIC_OBSERVATION | M | ROAD | 1 | Observation: total |
| R8 | **OCCURS_ON** | INCIDENT | M | ROAD | 1 | Incident: partial (nullable FK) |
| R9 | **OCCURS_AT** | INCIDENT | M | JUNCTION | 1 | Incident: partial (nullable FK) |
| R10 | **INVOLVES** | INCIDENT | M | VEHICLE | 1 | Incident: partial (nullable FK) |
| R11 | **INSTALLED_AT** | SENSOR | M | JUNCTION | 1 | Sensor: total |

---

## Section 4 — EER Specialisation Hierarchies

Draw these as **ISA triangles** below the supertype entity.

---

### ISA Hierarchy 1: VEHICLE Specialisation
**Type:** Total participation, Disjoint (`d` inside triangle)

```
           VEHICLE
              |
         [ISA / d]         ← draw as triangle with "d" inside
       /    |    |    \
     CAR  TRUCK MOTO  BUS
```

**CAR** extra attributes (ellipses connected to CAR rectangle):
- `num_doors`
- `fuel_type`

**TRUCK** extra attributes:
- `max_load_tonnes`

**MOTORCYCLE** extra attributes:
- `engine_cc`

**BUS** extra attributes:
- `seating_capacity`

> **Total participation** means every VEHICLE must be one of the subtypes.  
> **Disjoint** means a VEHICLE cannot be both a Car and a Truck.  
> Draw a **double line** from VEHICLE down to the ISA triangle.

---

### ISA Hierarchy 2: INCIDENT Specialisation
**Type:** Partial participation, Disjoint (`d` inside triangle)

```
           INCIDENT
              |
         [ISA / d]         ← draw as triangle with "d" inside
       /     |     |     \
  ACCIDENT BREAKDOWN ROADBLOCK FLOODING
```

**ACCIDENT** extra attributes:
- `injuries_count`
- `fatalities`

**BREAKDOWN** extra attributes:
- `breakdown_cause`

**ROADBLOCK** extra attributes:
- `authority_name`

**FLOODING** extra attributes:
- `water_level_cm`

> **Partial participation** means some INCIDENTs may not have a subtype entry.  
> Draw a **single line** from INCIDENT down to the ISA triangle.

---

## Section 5 — Suggested Layout for Drawing

Place entities in this rough grid layout to avoid crossing lines:

```
TOP ROW (left to right):
  ZONE

MIDDLE-LEFT:
  ROAD ──── ROAD_JUNCTION ──── JUNCTION
                                   |
                           TRAFFIC_SIGNAL    SENSOR

MIDDLE-RIGHT:
  DRIVER ──── VEHICLE
                  |
             [ISA Vehicle]
           CAR  TRUCK  MOTO  BUS

BOTTOM-LEFT:
  INCIDENT
      |
  [ISA Incident]
  ACCIDENT  BREAKDOWN  ROADBLOCK  FLOODING

BOTTOM-RIGHT:
  TRAFFIC_OBSERVATION
```

Relationship diamonds go **between** the two entities they connect.

---

## Section 6 — Ready-to-Paste AI Image Prompt

Copy the text below and paste it into **ChatGPT (with DALL·E)**, **Gemini**, **Ideogram**, or any AI image tool:

---

```
Draw a complete Entity-Relationship (ER) diagram for a traffic management database system 
called "Urban Traffic Management System". Use standard Chen notation with rectangles for 
entities, ellipses for attributes, underlined text for primary keys, and diamonds for 
relationships. Use ISA triangles for specialisation hierarchies.

The diagram must include these entities and attributes:

1. ZONE: zone_id (PK, underlined), zone_name, city, area_sqkm, zone_type
2. ROAD: road_id (PK), road_name, road_type, length_km, num_lanes, speed_limit, 
   surface_type, direction_type
3. JUNCTION: junction_id (PK), junction_name, junction_type, latitude, longitude, 
   signal_controlled, congestion_status
4. ROAD_JUNCTION (bridge/associative entity): road_id (composite PK), junction_id 
   (composite PK), position_type
5. TRAFFIC_SIGNAL: signal_id (PK), signal_type, installed_date, operational_status, 
   green_duration_sec
6. DRIVER: driver_id (PK), name, license_no (candidate key - dashed underline), 
   dob, contact, address
7. VEHICLE: vehicle_id (PK), license_plate (candidate key), vehicle_type, make, 
   model, year, registered_state
8. INCIDENT: incident_id (PK), incident_type, severity, description, 
   reported_datetime, resolved_datetime, reported_by
9. TRAFFIC_OBSERVATION: obs_id (PK), observation_time, vehicle_count, 
   avg_speed_kmph, congestion_level, weather_condition, data_source
10. SENSOR: sensor_id (PK), sensor_type, installation_date, status, 
    last_reading_time

Relationships (diamonds between entities with cardinality labels):
- ROAD M:1 ZONE (relationship: BELONGS_TO)
- JUNCTION M:1 ZONE (relationship: LOCATED_IN)
- ROAD M:N JUNCTION (relationship: CONNECTS, resolved via ROAD_JUNCTION bridge entity)
- JUNCTION 1:M TRAFFIC_SIGNAL (relationship: HAS_SIGNAL, total participation for signal)
- DRIVER 1:M VEHICLE (relationship: OWNS)
- TRAFFIC_OBSERVATION M:1 JUNCTION (relationship: OBSERVED_AT, total participation)
- TRAFFIC_OBSERVATION M:1 ROAD (relationship: RECORDED_ON, total participation)
- INCIDENT M:1 ROAD (relationship: OCCURS_ON, partial participation - nullable)
- INCIDENT M:1 JUNCTION (relationship: OCCURS_AT, partial participation - nullable)
- INCIDENT M:1 VEHICLE (relationship: INVOLVES, partial participation - nullable)
- SENSOR M:1 JUNCTION (relationship: INSTALLED_AT, total participation)

EER Specialisation hierarchies (ISA triangles with "d" for disjoint):
1. VEHICLE specialises into CAR (num_doors, fuel_type), TRUCK (max_load_tonnes), 
   MOTORCYCLE (engine_cc), BUS (seating_capacity). Total disjoint specialisation 
   (double line from VEHICLE to ISA triangle, "d" inside triangle).

2. INCIDENT specialises into ACCIDENT (injuries_count, fatalities), 
   BREAKDOWN (breakdown_cause), ROADBLOCK (authority_name), 
   FLOODING (water_level_cm). Partial disjoint specialisation 
   (single line from INCIDENT to ISA triangle, "d" inside triangle).

Layout suggestion: Place ZONE at top-centre. ROAD and JUNCTION in the middle row 
connected by ROAD_JUNCTION. TRAFFIC_SIGNAL and SENSOR below JUNCTION. 
DRIVER and VEHICLE on the right. INCIDENT and TRAFFIC_OBSERVATION at the bottom. 
ISA hierarchies below VEHICLE and INCIDENT respectively.

Use a clean white background, blue entity rectangles, light-grey attribute ellipses, 
yellow relationship diamonds. Make all text readable at A4 size.
```

---

## Section 7 — draw.io Step-by-Step Instructions

If using **draw.io** (diagrams.net):

1. Go to [https://app.diagrams.net](https://app.diagrams.net) → Create New Diagram → Blank
2. In the left panel search for: **"ERD"** — use the Entity shapes
3. For each entity: drag a **Rectangle** shape → type entity name → make text bold
4. For each attribute: drag an **Ellipse** → type attribute name → draw a line to the entity
5. For PK attributes: select the ellipse text → Format → underline
6. For relationships: drag a **Diamond** shape → type relationship name → connect lines to both entities → label lines with 1, M, or N near each entity
7. For ISA: draw an upward-pointing **Triangle** → type "ISA" → connect supertype entity to triangle top → connect each subtype entity to triangle bottom
8. For disjoint: add a small "d" text box inside the ISA triangle
9. Export: File → Export As → PNG (300 DPI) → save as `ER_Diagram.png` in the `docs/` folder

---

*BITS Pilani WILP | SESAP ZC337 | Urban Traffic Management System*
