-- Urban Road & Real-Time Traffic Management System
-- BITS Pilani WILP | SESAP ZC337
-- schema.sql — CREATE TABLE statements
-- Status: To be finalised after normalization (Phase 3)

-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- ZONE
CREATE TABLE Zone (
    zone_id       INTEGER PRIMARY KEY,
    zone_name     TEXT    NOT NULL,
    city          TEXT    NOT NULL,
    area_sqkm     REAL,
    zone_type     TEXT
);

-- ROAD
CREATE TABLE Road (
    road_id        INTEGER PRIMARY KEY,
    road_name      TEXT    NOT NULL,
    road_type      TEXT,
    length_km      REAL,
    num_lanes      INTEGER,
    speed_limit    INTEGER,
    surface_type   TEXT,
    direction_type TEXT,
    zone_id        INTEGER NOT NULL,
    FOREIGN KEY (zone_id) REFERENCES Zone(zone_id)
);

-- JUNCTION
CREATE TABLE Junction (
    junction_id      INTEGER PRIMARY KEY,
    junction_name    TEXT    NOT NULL,
    junction_type    TEXT,
    latitude         REAL,
    longitude        REAL,
    signal_controlled INTEGER DEFAULT 0,
    zone_id          INTEGER NOT NULL,
    FOREIGN KEY (zone_id) REFERENCES Zone(zone_id)
);

-- ROAD_JUNCTION (M:N bridge)
CREATE TABLE Road_Junction (
    road_id      INTEGER NOT NULL,
    junction_id  INTEGER NOT NULL,
    position_type TEXT,
    PRIMARY KEY (road_id, junction_id),
    FOREIGN KEY (road_id)     REFERENCES Road(road_id),
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id)
);

-- TRAFFIC_SIGNAL
CREATE TABLE Traffic_Signal (
    signal_id          INTEGER PRIMARY KEY,
    junction_id        INTEGER NOT NULL,
    signal_type        TEXT,
    installed_date     DATE,
    operational_status TEXT,
    green_duration_sec INTEGER,
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id)
);

-- DRIVER
CREATE TABLE Driver (
    driver_id  INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    license_no TEXT    UNIQUE,
    dob        DATE,
    contact    TEXT,
    address    TEXT
);

-- VEHICLE
CREATE TABLE Vehicle (
    vehicle_id       INTEGER PRIMARY KEY,
    license_plate    TEXT    UNIQUE NOT NULL,
    vehicle_type     TEXT,
    make             TEXT,
    model            TEXT,
    year             INTEGER,
    registered_state TEXT,
    owner_id         INTEGER,
    FOREIGN KEY (owner_id) REFERENCES Driver(driver_id)
);

-- INCIDENT
CREATE TABLE Incident (
    incident_id       INTEGER PRIMARY KEY,
    incident_type     TEXT    NOT NULL,
    severity          TEXT,
    description       TEXT,
    reported_datetime DATETIME NOT NULL,
    resolved_datetime DATETIME,
    road_id           INTEGER,
    junction_id       INTEGER,
    vehicle_id        INTEGER,
    reported_by       TEXT,
    FOREIGN KEY (road_id)     REFERENCES Road(road_id),
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id),
    FOREIGN KEY (vehicle_id)  REFERENCES Vehicle(vehicle_id)
);

-- TRAFFIC_OBSERVATION
CREATE TABLE Traffic_Observation (
    obs_id           INTEGER PRIMARY KEY,
    junction_id      INTEGER NOT NULL,
    road_id          INTEGER NOT NULL,
    observation_time DATETIME NOT NULL,
    vehicle_count    INTEGER,
    avg_speed_kmph   REAL,
    congestion_level TEXT,
    weather_condition TEXT,
    data_source      TEXT,
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id),
    FOREIGN KEY (road_id)     REFERENCES Road(road_id)
);

-- SENSOR
CREATE TABLE Sensor (
    sensor_id         INTEGER PRIMARY KEY,
    sensor_type       TEXT,
    junction_id       INTEGER NOT NULL,
    installation_date DATE,
    status            TEXT,
    last_reading_time DATETIME,
    FOREIGN KEY (junction_id) REFERENCES Junction(junction_id)
);
