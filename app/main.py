"""
Urban Road & Real-Time Traffic Management System
BITS Pilani WILP | SESAP ZC337
app/main.py — FastAPI Backend with PostgreSQL

DBSA Concepts Demonstrated:
  - Parameterized SQL (prevents SQL injection)
  - ACID transactions (BEGIN / COMMIT / ROLLBACK)
  - WAL recovery (PostgreSQL native WAL)
  - Role-based access control (X-User-Role header)
  - Input validation at system boundary
  - Connection pooling via psycopg2
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator

# ── App configuration ─────────────────────────────────────────────────────────

DB_CONFIG = {
    "host":     os.getenv("PGHOST",     "localhost"),
    "port":     int(os.getenv("PGPORT", "5432")),
    "dbname":   os.getenv("PGDATABASE", "traffic_db"),
    "user":     os.getenv("PGUSER",     "traffic_user"),
    "password": os.getenv("PGPASSWORD", "traffic_pass"),
}

from app.scheduler import start_scheduler

app = FastAPI(
    title="Urban Traffic Management System",
    description="BITS Pilani WILP | SESAP ZC337",
    version="3.0.0"
)

@app.on_event("startup")
def startup_event():
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database helpers ──────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetchall(conn, sql, params=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def fetchone(conn, sql, params=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur

# ── Role-based access control ─────────────────────────────────────────────────

ROLES = {'admin', 'officer', 'public'}


def get_role(x_user_role: Optional[str] = None) -> str:
    role = (x_user_role or "public").lower()
    return role if role in ROLES else "public"


def require_role(role: str, *allowed: str):
    if role not in allowed:
        raise HTTPException(status_code=403, detail=f"Forbidden — requires role: {list(allowed)}")

# ── Pydantic models ───────────────────────────────────────────────────────────

class TrafficObservationIn(BaseModel):
    junction_id: int
    road_id: int
    vehicle_count: int
    avg_speed_kmph: float
    congestion_level: str
    data_source: str
    weather_condition: Optional[str] = None

    @validator('congestion_level')
    def validate_congestion(cls, v):
        valid = {'LOW', 'MODERATE', 'HIGH', 'SEVERE'}
        if v.upper() not in valid:
            raise ValueError(f'congestion_level must be one of {valid}')
        return v.upper()

    @validator('data_source')
    def validate_source(cls, v):
        valid = {'Sensor', 'Manual', 'Camera', 'API'}
        if v not in valid:
            raise ValueError(f'data_source must be one of {valid}')
        return v

    @validator('weather_condition')
    def validate_weather(cls, v):
        if v is None:
            return v
        valid = {'Clear', 'Rainy', 'Foggy', 'Cloudy', 'Stormy'}
        if v not in valid:
            raise ValueError(f'weather_condition must be one of {valid}')
        return v


class IncidentIn(BaseModel):
    incident_type: str
    severity: str
    description: Optional[str] = None
    road_id: Optional[int] = None
    junction_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    reported_by: Optional[str] = "API"

    @validator('incident_type')
    def validate_type(cls, v):
        valid = {'Accident', 'Breakdown', 'Roadblock', 'Flooding'}
        if v not in valid:
            raise ValueError(f'incident_type must be one of {valid}')
        return v

    @validator('severity')
    def validate_severity(cls, v):
        valid = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}
        if v.upper() not in valid:
            raise ValueError(f'severity must be one of {valid}')
        return v.upper()


class IncidentUpdate(BaseModel):
    severity: Optional[str] = None
    description: Optional[str] = None
    resolved_datetime: Optional[str] = None
    reported_by: Optional[str] = None


class SensorReadingIn(BaseModel):
    sensor_id: int
    vehicle_count: int
    avg_speed: float
    raw_payload: Optional[dict] = None

    @validator('vehicle_count')
    def validate_count(cls, v):
        if v < 0:
            raise ValueError('vehicle_count must be >= 0')
        return v

    @validator('avg_speed')
    def validate_speed(cls, v):
        if v < 0:
            raise ValueError('avg_speed must be >= 0')
        return v


class SignalOverrideIn(BaseModel):
    green_duration_sec: int

    @validator('green_duration_sec')
    def validate_duration(cls, v):
        if not (5 <= v <= 300):
            raise ValueError('green_duration_sec must be between 5 and 300')
        return v


class PublicIncidentIn(BaseModel):
    incident_type: str
    description: Optional[str] = None
    junction_id: Optional[int] = None
    road_id: Optional[int] = None

    @validator('incident_type')
    def validate_type(cls, v):
        valid = {'Accident', 'Breakdown', 'Roadblock', 'Flooding'}
        if v not in valid:
            raise ValueError(f'incident_type must be one of {valid}')
        return v

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    try:
        with get_db() as conn:
            fetchone(conn, "SELECT 1 AS ok")
        return {"status": "ok", "db": DB_CONFIG["dbname"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── ZONES ─────────────────────────────────────────────────────────────────────

@app.get("/api/zones")
def get_zones():
    with get_db() as conn:
        return fetchall(conn, "SELECT * FROM Zone ORDER BY zone_name")

# ── ROADS ─────────────────────────────────────────────────────────────────────

@app.get("/api/roads")
def get_roads(zone_id: Optional[int] = None, road_type: Optional[str] = None):
    sql = "SELECT r.*, z.zone_name FROM Road r JOIN Zone z ON r.zone_id = z.zone_id WHERE 1=1"
    params = []
    if zone_id:
        sql += " AND r.zone_id = %s"
        params.append(zone_id)
    if road_type:
        sql += " AND r.road_type = %s"
        params.append(road_type)
    sql += " ORDER BY r.road_name"
    with get_db() as conn:
        return fetchall(conn, sql, params)


@app.get("/api/roads/{road_id}")
def get_road(road_id: int):
    with get_db() as conn:
        row = fetchone(conn,
            "SELECT r.*, z.zone_name FROM Road r JOIN Zone z ON r.zone_id = z.zone_id WHERE r.road_id = %s",
            (road_id,))
    if row is None:
        raise HTTPException(status_code=404, detail="Road not found")
    return row

# ── JUNCTIONS ─────────────────────────────────────────────────────────────────

@app.get("/api/junctions")
def get_junctions(zone_id: Optional[int] = None):
    sql = "SELECT j.*, z.zone_name FROM Junction j JOIN Zone z ON j.zone_id = z.zone_id WHERE 1=1"
    params = []
    if zone_id:
        sql += " AND j.zone_id = %s"
        params.append(zone_id)
    sql += " ORDER BY j.junction_name"
    with get_db() as conn:
        return fetchall(conn, sql, params)

# ── TRAFFIC OBSERVATIONS ──────────────────────────────────────────────────────

@app.get("/api/traffic")
def get_traffic(
    junction_id: Optional[int] = None,
    road_id: Optional[int] = None,
    congestion_level: Optional[str] = None,
    hours: int = 24,
    limit: int = 100
):
    limit = min(limit, 500)
    sql = """
        SELECT t.*, j.junction_name, r.road_name, z.zone_name
        FROM Traffic_Observation t
        JOIN Junction j ON t.junction_id = j.junction_id
        JOIN Road     r ON t.road_id     = r.road_id
        JOIN Zone     z ON j.zone_id     = z.zone_id
        WHERE t.observation_time >= NOW() - (%s || ' hours')::INTERVAL
    """
    params: list = [hours]
    if junction_id:
        sql += " AND t.junction_id = %s"
        params.append(junction_id)
    if road_id:
        sql += " AND t.road_id = %s"
        params.append(road_id)
    if congestion_level:
        sql += " AND t.congestion_level = %s"
        params.append(congestion_level.upper())
    sql += " ORDER BY t.observation_time DESC LIMIT %s"
    params.append(limit)
    with get_db() as conn:
        return fetchall(conn, sql, params)


@app.get("/api/traffic/road/{road_id_path}")
def get_traffic_by_road(road_id_path: int):
    with get_db() as conn:
        return fetchall(conn, """
            SELECT t.*, j.junction_name, r.road_name
            FROM Traffic_Observation t
            JOIN Junction j ON t.junction_id = j.junction_id
            JOIN Road     r ON t.road_id     = r.road_id
            WHERE t.road_id = %s
            ORDER BY t.observation_time DESC LIMIT 50
        """, (road_id_path,))


@app.post("/api/traffic", status_code=201)
def post_traffic(data: TrafficObservationIn, x_user_role: Optional[str] = Header(default="public")):
    role = get_role(x_user_role)
    require_role(role, 'officer', 'admin')

    with get_db() as conn:
        if not fetchone(conn, "SELECT junction_id FROM Junction WHERE junction_id = %s", (data.junction_id,)):
            raise HTTPException(status_code=400, detail=f"junction_id {data.junction_id} does not exist")
        if not fetchone(conn, "SELECT road_id FROM Road WHERE road_id = %s", (data.road_id,)):
            raise HTTPException(status_code=400, detail=f"road_id {data.road_id} does not exist")

        # ACID Transaction T1: INSERT observation
        # trg_congestion_alert trigger handles junction congestion update atomically
        # 2PL Growing phase: acquire write lock on Traffic_Observation
        try:
            cur = execute(conn, """
                INSERT INTO Traffic_Observation
                    (junction_id, road_id, observation_time, vehicle_count,
                     avg_speed_kmph, congestion_level, weather_condition, data_source)
                VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
                RETURNING obs_id
            """, (
                data.junction_id, data.road_id,
                data.vehicle_count, data.avg_speed_kmph,
                data.congestion_level, data.weather_condition, data.data_source
            ))
            obs_id = cur.fetchone()[0]
            # 2PL Shrinking phase: COMMIT releases all locks
        except psycopg2.errors.ForeignKeyViolation as e:
            raise HTTPException(status_code=400, detail=f"FK violation: {e}")

    return {"message": "Observation recorded", "obs_id": obs_id}

# ── SENSOR READINGS ───────────────────────────────────────────────────────────

@app.post("/api/sensors/reading", status_code=201)
def post_sensor_reading(data: SensorReadingIn):
    """Ingest a raw sensor reading into Sensor_Reading table."""
    import json
    with get_db() as conn:
        try:
            cur = execute(conn, """
                INSERT INTO Sensor_Reading
                    (sensor_id, read_time, vehicle_count, avg_speed, raw_payload)
                VALUES (%s, NOW(), %s, %s, %s)
                RETURNING reading_id
            """, (
                data.sensor_id,
                data.vehicle_count,
                data.avg_speed,
                json.dumps(data.raw_payload) if data.raw_payload else None,
            ))
            reading_id = cur.fetchone()[0]
        except psycopg2.errors.ForeignKeyViolation:
            cur = execute(conn, """
                INSERT INTO Sensor_Reading
                    (read_time, vehicle_count, avg_speed, raw_payload)
                VALUES (NOW(), %s, %s, %s)
                RETURNING reading_id
            """, (
                data.vehicle_count,
                data.avg_speed,
                json.dumps(data.raw_payload) if data.raw_payload else None,
            ))
            reading_id = cur.fetchone()[0]
    return {"message": "Reading recorded", "reading_id": reading_id}

# ── INCIDENTS ─────────────────────────────────────────────────────────────────

@app.get("/api/incidents")
def get_incidents(
    severity: Optional[str] = None,
    road_id: Optional[int] = None,
    zone_id: Optional[int] = None,
    open_only: bool = True,
    limit: int = 50
):
    limit = min(limit, 200)
    sql = """
        SELECT i.*, r.road_name, j.junction_name,
               COALESCE(rz.zone_name, jz.zone_name) AS zone_name,
               v.license_plate
        FROM Incident i
        LEFT JOIN Road    r  ON i.road_id     = r.road_id
        LEFT JOIN Zone    rz ON r.zone_id     = rz.zone_id
        LEFT JOIN Junction j  ON i.junction_id = j.junction_id
        LEFT JOIN Zone    jz ON j.zone_id     = jz.zone_id
        LEFT JOIN Vehicle v  ON i.vehicle_id  = v.vehicle_id
        WHERE 1=1
    """
    params: list = []
    if open_only:
        sql += " AND i.resolved_datetime IS NULL"
    if severity:
        sql += " AND i.severity = %s"
        params.append(severity.upper())
    if road_id:
        sql += " AND i.road_id = %s"
        params.append(road_id)
    if zone_id:
        sql += " AND (rz.zone_id = %s OR jz.zone_id = %s)"
        params += [zone_id, zone_id]
    sql += """
        ORDER BY CASE i.severity
            WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM' THEN 3 ELSE 4 END,
        i.reported_datetime DESC LIMIT %s
    """
    params.append(limit)
    with get_db() as conn:
        return fetchall(conn, sql, params)


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: int):
    with get_db() as conn:
        row = fetchone(conn, """
            SELECT i.*, r.road_name, j.junction_name,
                   COALESCE(rz.zone_name, jz.zone_name) AS zone_name,
                   v.license_plate, v.vehicle_type
            FROM Incident i
            LEFT JOIN Road     r  ON i.road_id     = r.road_id
            LEFT JOIN Zone     rz ON r.zone_id     = rz.zone_id
            LEFT JOIN Junction j  ON i.junction_id = j.junction_id
            LEFT JOIN Zone     jz ON j.zone_id     = jz.zone_id
            LEFT JOIN Vehicle  v  ON i.vehicle_id  = v.vehicle_id
            WHERE i.incident_id = %s
        """, (incident_id,))
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return row


@app.post("/api/incidents", status_code=201)
def post_incident(data: IncidentIn, x_user_role: Optional[str] = Header(default="public")):
    role = get_role(x_user_role)
    require_role(role, 'officer', 'admin')

    with get_db() as conn:
        try:
            cur = execute(conn, """
                INSERT INTO Incident
                    (incident_type, severity, description,
                     reported_datetime, road_id, junction_id, vehicle_id, reported_by)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)
                RETURNING incident_id
            """, (
                data.incident_type, data.severity, data.description,
                data.road_id, data.junction_id, data.vehicle_id, data.reported_by
            ))
            inc_id = cur.fetchone()[0]
        except psycopg2.errors.ForeignKeyViolation as e:
            raise HTTPException(status_code=400, detail=f"FK violation: {e}")

    return {"message": "Incident reported", "incident_id": inc_id}


@app.put("/api/incidents/{incident_id}")
def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    x_user_role: Optional[str] = Header(default="public")
):
    role = get_role(x_user_role)
    require_role(role, 'officer', 'admin')

    with get_db() as conn:
        row = fetchone(conn, "SELECT * FROM Incident WHERE incident_id = %s", (incident_id,))
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        updates = {k: v for k, v in data.dict().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=400, detail="No updatable fields provided")

        if 'resolved_datetime' in updates:
            try:
                res_dt = datetime.fromisoformat(updates['resolved_datetime'])
                rep_dt = row['reported_datetime']
                if isinstance(rep_dt, str):
                    rep_dt = datetime.fromisoformat(rep_dt)
                if res_dt < rep_dt:
                    raise HTTPException(status_code=400, detail="resolved_datetime cannot be before reported_datetime")
            except ValueError:
                raise HTTPException(status_code=400, detail="resolved_datetime must be ISO 8601 format")

        set_clause = ', '.join(f"{k} = %s" for k in updates)
        values = list(updates.values()) + [incident_id]

        cur = execute(conn, f"UPDATE Incident SET {set_clause} WHERE incident_id = %s", values)
        if cur.rowcount != 1:
            raise HTTPException(status_code=500, detail="Update affected unexpected number of rows")

    return {"message": "Incident updated", "incident_id": incident_id}


@app.delete("/api/incidents/{incident_id}")
def delete_incident(incident_id: int, x_user_role: Optional[str] = Header(default="public")):
    role = get_role(x_user_role)
    require_role(role, 'admin')

    with get_db() as conn:
        row = fetchone(conn, "SELECT incident_id FROM Incident WHERE incident_id = %s", (incident_id,))
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        execute(conn, "DELETE FROM Incident WHERE incident_id = %s", (incident_id,))

    return {"message": "Incident deleted", "incident_id": incident_id}

# ── MAP DATA ──────────────────────────────────────────────────────────────────

@app.get("/api/map")
def get_map_data():
    with get_db() as conn:
        junctions = fetchall(conn, """
            SELECT
                j.junction_id, j.junction_name, j.latitude, j.longitude,
                j.junction_type, j.congestion_status, z.zone_name,
                t.congestion_level, t.vehicle_count, t.avg_speed_kmph,
                t.observation_time, t.weather_condition,
                ts.operational_status AS signal_status
            FROM Junction j
            JOIN Zone z ON j.zone_id = z.zone_id
            LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
                AND t.observation_time = (
                    SELECT MAX(t2.observation_time)
                    FROM Traffic_Observation t2
                    WHERE t2.junction_id = j.junction_id
                )
            LEFT JOIN Traffic_Signal ts ON j.junction_id = ts.junction_id
                AND ts.operational_status = 'Active'
            WHERE j.latitude IS NOT NULL AND j.longitude IS NOT NULL
            ORDER BY j.junction_name
        """)
        incidents = fetchall(conn, """
            SELECT i.incident_id, i.incident_type, i.severity, i.description,
                   i.reported_datetime, r.road_name, j.junction_name,
                   j.latitude, j.longitude
            FROM Incident i
            LEFT JOIN Junction j ON i.junction_id = j.junction_id
            LEFT JOIN Road r     ON i.road_id     = r.road_id
            WHERE i.resolved_datetime IS NULL
              AND j.latitude IS NOT NULL AND j.longitude IS NOT NULL
            ORDER BY CASE i.severity
                WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3 ELSE 4 END
        """)
    return {"junctions": junctions, "incidents": incidents}

# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard():
    with get_db() as conn:
        junctions = fetchall(conn, "SELECT * FROM TrafficDashboard ORDER BY congestion_level DESC NULLS LAST")
        zones = fetchall(conn, "SELECT * FROM ZoneSummary ORDER BY zone_name")
        kpis = fetchone(conn, """
            SELECT
                COUNT(*) AS total_observations_24h,
                ROUND(AVG(vehicle_count)::NUMERIC, 0) AS city_avg_vehicles,
                ROUND(AVG(avg_speed_kmph)::NUMERIC, 1) AS city_avg_speed,
                SUM(CASE WHEN congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END) AS high_congestion_count
            FROM Traffic_Observation
            WHERE observation_time >= NOW() - INTERVAL '1 day'
        """)
        incident_summary = fetchall(conn, """
            SELECT severity, COUNT(*) AS count
            FROM Incident
            WHERE resolved_datetime IS NULL
            GROUP BY severity
            ORDER BY CASE severity
                WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3 ELSE 4 END
        """)
    return {
        "junctions":        junctions,
        "zones":            zones,
        "city_kpis":        kpis or {},
        "incident_summary": incident_summary
    }

# ── ANALYTICS ─────────────────────────────────────────────────────────────────

@app.get("/api/analytics/peak-hours")
def peak_hours():
    with get_db() as conn:
        return fetchall(conn, """
            SELECT
                TO_CHAR(observation_time, 'HH24') AS hour_of_day,
                COUNT(*) AS total_observations,
                ROUND(AVG(vehicle_count)::NUMERIC, 0) AS avg_vehicles,
                SUM(CASE WHEN congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END) AS high_congestion_obs
            FROM Traffic_Observation
            GROUP BY hour_of_day
            ORDER BY avg_vehicles DESC
        """)


@app.get("/api/analytics/zone-summary")
def zone_summary():
    with get_db() as conn:
        return fetchall(conn, "SELECT * FROM ZoneSummary ORDER BY zone_name")


@app.get("/api/analytics/top-congested")
def top_congested():
    with get_db() as conn:
        return fetchall(conn, """
            SELECT j.junction_name, z.zone_name,
                   COUNT(t.obs_id) AS obs_count,
                   ROUND(AVG(t.vehicle_count)::NUMERIC, 0) AS avg_vehicles,
                   ROUND(AVG(t.avg_speed_kmph)::NUMERIC, 1) AS avg_speed
            FROM Traffic_Observation t
            INNER JOIN Junction j ON t.junction_id = j.junction_id
            INNER JOIN Zone     z ON j.zone_id     = z.zone_id
            WHERE t.observation_time >= NOW() - INTERVAL '1 day'
            GROUP BY j.junction_id, j.junction_name, z.zone_name
            ORDER BY avg_vehicles DESC
            LIMIT 5
        """)

# ── AUDIT LOG (admin only) ────────────────────────────────────────────────────

@app.get("/api/audit")
def get_audit_log(x_user_role: Optional[str] = Header(default="public")):
    role = get_role(x_user_role)
    require_role(role, 'admin')
    with get_db() as conn:
        return fetchall(conn, "SELECT * FROM Incident_Audit ORDER BY changed_at DESC LIMIT 100")

# ── SIGNAL OVERRIDE ───────────────────────────────────────────────────────────

@app.post("/api/signals/{signal_id}/override")
def override_signal(
    signal_id: int,
    data: SignalOverrideIn,
    x_user_role: Optional[str] = Header(default="public")
):
    """Manually override a traffic signal's green phase duration (admin only)."""
    role = get_role(x_user_role)
    require_role(role, 'admin')

    with get_db() as conn:
        row = fetchone(conn,
            "SELECT signal_id FROM Traffic_Signal WHERE signal_id = %s", (signal_id,))
        if row is None:
            raise HTTPException(status_code=404, detail="Signal not found")
        execute(conn,
            "UPDATE Traffic_Signal SET green_duration_sec = %s WHERE signal_id = %s",
            (data.green_duration_sec, signal_id))

    return {"message": "Signal overridden", "signal_id": signal_id,
            "green_duration_sec": data.green_duration_sec}


@app.get("/api/signals")
def get_signals(junction_id: Optional[int] = None):
    """List all traffic signals with their current green_duration_sec."""
    sql = """
        SELECT ts.*, j.junction_name, z.zone_name
        FROM Traffic_Signal ts
        JOIN Junction j ON ts.junction_id = j.junction_id
        JOIN Zone z     ON j.zone_id      = z.zone_id
        WHERE 1=1
    """
    params = []
    if junction_id:
        sql += " AND ts.junction_id = %s"
        params.append(junction_id)
    sql += " ORDER BY j.junction_name"
    with get_db() as conn:
        return fetchall(conn, sql, params)


# ── NEARBY JUNCTIONS (PostGIS spatial query) ──────────────────────────────────

@app.get("/api/junctions/nearby")
def get_nearby_junctions(lat: float, lon: float, radius_km: float = 2.0):
    """Find junctions within radius_km of a given lat/lon using PostGIS."""
    with get_db() as conn:
        col = fetchone(conn, """
            SELECT column_name FROM information_schema.columns
            WHERE table_name='junction' AND column_name='geom'
        """)
        if col is None:
            return fetchall(conn, """
                SELECT j.*, z.zone_name,
                    ROUND((
                        111.0 * SQRT(
                            POWER(j.latitude  - %s, 2) +
                            POWER(j.longitude - %s, 2)
                        )
                    )::NUMERIC, 2) AS distance_km
                FROM Junction j
                JOIN Zone z ON j.zone_id = z.zone_id
                WHERE j.latitude IS NOT NULL
                ORDER BY distance_km
                LIMIT 10
            """, (lat, lon))

        return fetchall(conn, """
            SELECT j.*, z.zone_name,
                ROUND(
                    (ST_Distance(j.geom, ST_MakePoint(%s, %s)::GEOGRAPHY) / 1000)::NUMERIC,
                    2
                ) AS distance_km
            FROM Junction j
            JOIN Zone z ON j.zone_id = z.zone_id
            WHERE j.geom IS NOT NULL
              AND ST_DWithin(j.geom, ST_MakePoint(%s, %s)::GEOGRAPHY, %s)
            ORDER BY distance_km
        """, (lon, lat, lon, lat, radius_km * 1000))


# ── PUBLIC CITIZEN INCIDENT REPORT (no auth required) ────────────────────────

@app.post("/api/incidents/report", status_code=201)
def report_incident_public(data: PublicIncidentIn):
    """Public endpoint — citizens can report incidents without authentication."""
    with get_db() as conn:
        try:
            cur = execute(conn, """
                INSERT INTO Incident
                    (incident_type, severity, description,
                     reported_datetime, road_id, junction_id, reported_by)
                VALUES (%s, 'MEDIUM', %s, NOW(), %s, %s, 'Citizen')
                RETURNING incident_id
            """, (
                data.incident_type, data.description,
                data.road_id, data.junction_id,
            ))
            inc_id = cur.fetchone()[0]
        except psycopg2.errors.ForeignKeyViolation as e:
            raise HTTPException(status_code=400, detail=f"Invalid junction_id or road_id: {e}")

    return {"message": "Incident reported — thank you!", "incident_id": inc_id}

