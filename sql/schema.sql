-- ============================================================
-- Urban Road & Real-Time Traffic Management System
-- BITS Pilani WILP | SESAP ZC337
-- schema.sql — PostgreSQL DDL: Tables, Indexes, Constraints
-- DBSA Concepts Covered: Three-schema architecture (internal),
--   ER-to-Relational mapping (all 7 rules), BCNF normalization,
--   B+ Tree indexing, Hash indexing, Data integrity constraints
-- ============================================================

-- ============================================================
-- ZONE  (Strong entity, Rule 1)
-- ============================================================
CREATE TABLE IF NOT EXISTS Zone (
    zone_id    SERIAL PRIMARY KEY,
    zone_name  TEXT    NOT NULL,
    city       TEXT    NOT NULL DEFAULT 'Bengaluru',
    area_sqkm  REAL    CHECK (area_sqkm > 0),
    zone_type  TEXT    CHECK (zone_type IN ('Residential','Commercial','Industrial','Mixed','IT Corridor'))
);

-- ============================================================
-- ROAD  (Strong entity, Rule 1 + 1:N with Zone, Rule 4)
-- ============================================================
CREATE TABLE IF NOT EXISTS Road (
    road_id        SERIAL PRIMARY KEY,
    road_name      TEXT    NOT NULL,
    road_type      TEXT    CHECK (road_type IN ('National Highway','State Highway','City Road','Ring Road','Lane','Flyover')),
    length_km      REAL    CHECK (length_km > 0),
    num_lanes      INTEGER CHECK (num_lanes > 0),
    speed_limit    INTEGER CHECK (speed_limit BETWEEN 10 AND 120),
    surface_type   TEXT    CHECK (surface_type IN ('Asphalt','Concrete','Gravel','Mixed')),
    direction_type TEXT    CHECK (direction_type IN ('One-way','Two-way','Divided')),
    zone_id        INTEGER NOT NULL,
    FOREIGN KEY (zone_id) REFERENCES Zone(zone_id) ON DELETE RESTRICT
);

-- ============================================================
-- JUNCTION  (Strong entity, Rule 1 + 1:N with Zone, Rule 4)
-- ============================================================
CREATE TABLE IF NOT EXISTS Junction (
    junction_id      SERIAL PRIMARY KEY,
    junction_name    TEXT    NOT NULL,
    junction_type    TEXT    CHECK (junction_type IN ('Signalised','Unsignalised','Roundabout','Flyover','Underpass')),
    latitude         REAL    CHECK (latitude  BETWEEN 12.7 AND 13.2),
    longitude        REAL    CHECK (longitude BETWEEN 77.4 AND 77.8),
    signal_controlled INTEGER DEFAULT 0 CHECK (signal_controlled IN (0,1)),
    congestion_status TEXT   DEFAULT 'NORMAL' CHECK (congestion_status IN ('NORMAL','HIGH')),
    zone_id          INTEGER NOT NULL,
    FOREIGN KEY (zone_id) REFERENCES Zone(zone_id) ON DELETE RESTRICT
);

-- ============================================================
-- ROAD_JUNCTION  (M:N bridge table, Rule 5)
-- ============================================================
CREATE TABLE IF NOT EXISTS Road_Junction (
    road_id       INTEGER NOT NULL,
    junction_id   INTEGER NOT NULL,
    position_type TEXT    CHECK (position_type IN ('Start','End','Intermediate')),
    PRIMARY KEY (road_id, junction_id),
    FOREIGN KEY (road_id)     REFERENCES Road(road_id)     ON DELETE CASCADE,
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id) ON DELETE CASCADE
);

-- ============================================================
-- TRAFFIC_SIGNAL  (Strong entity + 1:N with Junction, Rule 4)
-- ============================================================
CREATE TABLE IF NOT EXISTS Traffic_Signal (
    signal_id          SERIAL PRIMARY KEY,
    junction_id        INTEGER NOT NULL,
    signal_type        TEXT    CHECK (signal_type IN ('Standard','Adaptive','Pedestrian','Emergency')),
    installed_date     DATE,
    operational_status TEXT    CHECK (operational_status IN ('Active','Inactive','Faulty','Under Maintenance')),
    green_duration_sec INTEGER CHECK (green_duration_sec > 0),
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id) ON DELETE RESTRICT
);

-- ============================================================
-- DRIVER  (Strong entity, Rule 1)
-- ============================================================
CREATE TABLE IF NOT EXISTS Driver (
    driver_id  SERIAL PRIMARY KEY,
    name       TEXT    NOT NULL,
    license_no TEXT    UNIQUE NOT NULL,
    dob        DATE,
    contact    TEXT,
    address    TEXT
);

-- ============================================================
-- VEHICLE  (Strong entity, Rule 1 + 1:N with Driver, Rule 4)
-- Hash-equivalent index on license_plate for O(1) exact lookup
-- ============================================================
CREATE TABLE IF NOT EXISTS Vehicle (
    vehicle_id       SERIAL PRIMARY KEY,
    license_plate    TEXT    UNIQUE NOT NULL,
    vehicle_type     TEXT    CHECK (vehicle_type IN ('Car','Truck','Motorcycle','Bus','Auto','Other')),
    make             TEXT,
    model            TEXT,
    year             INTEGER CHECK (year BETWEEN 1990 AND 2030),
    registered_state TEXT    DEFAULT 'Karnataka',
    owner_id         INTEGER,
    FOREIGN KEY (owner_id) REFERENCES Driver(driver_id) ON DELETE SET NULL
);

-- ============================================================
-- INCIDENT  (Strong entity + multi-FK 1:N, Rules 1+4)
-- Nullable FKs model partial participation in relationships
-- ============================================================
CREATE TABLE IF NOT EXISTS Incident (
    incident_id       SERIAL PRIMARY KEY,
    incident_type     TEXT    NOT NULL CHECK (incident_type IN ('Accident','Breakdown','Roadblock','Flooding')),
    severity          TEXT    CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    description       TEXT,
    reported_datetime TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_datetime TIMESTAMP,
    road_id           INTEGER,
    junction_id       INTEGER,
    vehicle_id        INTEGER,
    reported_by       TEXT,
    FOREIGN KEY (road_id)     REFERENCES Road(road_id)         ON DELETE SET NULL,
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id)  REFERENCES Vehicle(vehicle_id)   ON DELETE SET NULL
);

-- ============================================================
-- TRAFFIC_OBSERVATION  (Strong entity + 1:N with Junction+Road)
-- Core table demonstrating normalization (see SRS Section 4.3)
-- ============================================================
CREATE TABLE IF NOT EXISTS Traffic_Observation (
    obs_id            SERIAL PRIMARY KEY,
    junction_id       INTEGER NOT NULL,
    road_id           INTEGER NOT NULL,
    observation_time  TIMESTAMP NOT NULL DEFAULT NOW(),
    vehicle_count     INTEGER  CHECK (vehicle_count >= 0),
    avg_speed_kmph    REAL     CHECK (avg_speed_kmph >= 0),
    congestion_level  TEXT     CHECK (congestion_level IN ('LOW','MODERATE','HIGH','SEVERE')),
    weather_condition TEXT     CHECK (weather_condition IN ('Clear','Rainy','Foggy','Cloudy','Stormy')),
    data_source       TEXT     CHECK (data_source IN ('Sensor','Manual','Camera','API')),
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id) ON DELETE RESTRICT,
    FOREIGN KEY (road_id)     REFERENCES Road(road_id)         ON DELETE RESTRICT
);

-- ============================================================
-- SENSOR  (Strong entity + 1:N with Junction, Rule 4)
-- ============================================================
CREATE TABLE IF NOT EXISTS Sensor (
    sensor_id         SERIAL PRIMARY KEY,
    sensor_type       TEXT    CHECK (sensor_type IN ('Inductive Loop','Camera','Radar','CCTV','Microwave')),
    junction_id       INTEGER NOT NULL,
    installation_date DATE,
    status            TEXT    CHECK (status IN ('Active','Inactive','Faulty')),
    last_reading_time TIMESTAMP,
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id) ON DELETE RESTRICT
);

-- ============================================================
-- EER SPECIALISATION TABLES (ISA hierarchy, one table per subtype)
-- Supertype PK used as PK+FK in subtype (overlapping PKs)
-- ============================================================

CREATE TABLE IF NOT EXISTS Vehicle_Car (
    vehicle_id  INTEGER PRIMARY KEY,
    num_doors   INTEGER DEFAULT 4,
    fuel_type   TEXT    CHECK (fuel_type IN ('Petrol','Diesel','Electric','CNG','Hybrid')),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Vehicle_Truck (
    vehicle_id       INTEGER PRIMARY KEY,
    max_load_tonnes  REAL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Vehicle_Motorcycle (
    vehicle_id  INTEGER PRIMARY KEY,
    engine_cc   INTEGER,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Vehicle_Bus (
    vehicle_id        INTEGER PRIMARY KEY,
    seating_capacity  INTEGER,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Incident_Accident (
    incident_id    INTEGER PRIMARY KEY,
    injuries_count INTEGER DEFAULT 0,
    fatalities     INTEGER DEFAULT 0,
    FOREIGN KEY (incident_id) REFERENCES Incident(incident_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Incident_Breakdown (
    incident_id     INTEGER PRIMARY KEY,
    breakdown_cause TEXT,
    FOREIGN KEY (incident_id) REFERENCES Incident(incident_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Incident_Roadblock (
    incident_id    INTEGER PRIMARY KEY,
    authority_name TEXT,
    FOREIGN KEY (incident_id) REFERENCES Incident(incident_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Incident_Flooding (
    incident_id    INTEGER PRIMARY KEY,
    water_level_cm REAL,
    FOREIGN KEY (incident_id) REFERENCES Incident(incident_id) ON DELETE CASCADE
);

-- ============================================================
-- AUDIT LOG TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS Incident_Audit (
    audit_id       SERIAL PRIMARY KEY,
    incident_id    INTEGER,
    action         TEXT,
    old_severity   TEXT,
    new_severity   TEXT,
    changed_at     TIMESTAMP DEFAULT NOW(),
    changed_by     TEXT
);

-- ============================================================
-- INDEXES
-- B+ Tree: range queries, JOINs, ORDER BY
-- Hash-equivalent: UNIQUE constraints for exact-match lookups
-- ============================================================

-- B+ Tree: composite index for most common query (junction + time range)
CREATE INDEX IF NOT EXISTS idx_obs_junction_time ON Traffic_Observation(junction_id, observation_time);

-- B+ Tree: road-based observation queries
CREATE INDEX IF NOT EXISTS idx_obs_road ON Traffic_Observation(road_id);

-- B+ Tree: incident search by road
CREATE INDEX IF NOT EXISTS idx_incident_road ON Incident(road_id);

-- B+ Tree: incident search by junction
CREATE INDEX IF NOT EXISTS idx_incident_junction ON Incident(junction_id);

-- B+ Tree: incident date-range search
CREATE INDEX IF NOT EXISTS idx_incident_datetime ON Incident(reported_datetime);

-- B+ Tree: zone-based road queries
CREATE INDEX IF NOT EXISTS idx_road_zone ON Road(zone_id);

-- B+ Tree: zone-based junction queries
CREATE INDEX IF NOT EXISTS idx_junction_zone ON Junction(zone_id);

-- Hash-equivalent (UNIQUE): vehicle plate lookup — O(log n) in PostgreSQL, O(1) conceptually
CREATE INDEX IF NOT EXISTS idx_vehicle_plate ON Vehicle(license_plate);
CREATE INDEX IF NOT EXISTS idx_driver_license ON Driver(license_no);

-- ============================================================
-- ROLE-BASED ACCESS CONTROL
-- PostgreSQL native GRANT/REVOKE (replaces header simulation)
-- ============================================================

-- Create roles (ignore error if already exists)
DO $$ BEGIN
    CREATE ROLE admin_role;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE ROLE officer_role;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE ROLE public_role;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- admin_role: full access
GRANT ALL ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO admin_role;

-- officer_role: read all + write observations + write/update incidents (no delete)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO officer_role;
GRANT INSERT, UPDATE ON Traffic_Observation TO officer_role;
GRANT INSERT, UPDATE ON Incident TO officer_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO officer_role;

-- public_role: read-only on non-PII views
GRANT SELECT ON Zone, Road, Junction, Traffic_Observation TO public_role;
REVOKE SELECT ON Vehicle FROM public_role;
REVOKE SELECT ON Driver FROM public_role;

-- ============================================================
-- POSTGIS SPATIAL EXTENSION
-- ============================================================
CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE Junction ADD COLUMN IF NOT EXISTS geom GEOGRAPHY(POINT, 4326);

CREATE INDEX IF NOT EXISTS idx_junction_geom ON Junction USING GIST(geom);

-- ============================================================
-- SENSOR_READING  (time-series raw readings)
-- ============================================================
CREATE TABLE IF NOT EXISTS Sensor_Reading (
    reading_id    SERIAL PRIMARY KEY,
    sensor_id     INTEGER REFERENCES Sensor(sensor_id) ON DELETE CASCADE,
    read_time     TIMESTAMP NOT NULL DEFAULT NOW(),
    vehicle_count INTEGER   CHECK (vehicle_count >= 0),
    avg_speed     REAL      CHECK (avg_speed >= 0),
    raw_payload   JSONB
);

CREATE INDEX IF NOT EXISTS idx_sensor_reading_time
    ON Sensor_Reading(sensor_id, read_time);
