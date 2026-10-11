"""
Urban Road & Real-Time Traffic Management System
BITS Pilani WILP | SESAP ZC337
app/app.py — Flask REST API Backend

DBSA Concepts Demonstrated:
  - Parameterized SQL (prevents SQL injection)
  - ACID transactions (BEGIN / COMMIT / ROLLBACK)
  - WAL mode + FK enforcement via PRAGMA
  - Role-based access control (X-User-Role header)
  - Input validation at system boundary
  - Connection-per-request pattern (thread-safe for SQLite)
"""

import sqlite3
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, abort, g, render_template, send_from_directory

# ── App configuration ─────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DB_PATH      = os.path.join(BASE_DIR, '..', 'data', 'traffic.db')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR   = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['DB_PATH'] = DB_PATH

# ── Database helpers ──────────────────────────────────────────────────────────

def get_db():
    """Return a per-request SQLite connection with FK + WAL enabled."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row          # column-name access
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def rows_to_list(rows):
    return [dict(r) for r in rows]

# ── Role-based access control ─────────────────────────────────────────────────
# Roles: admin | officer | public
# Enforced via X-User-Role request header (simulates auth layer)

ROLES = {'admin', 'officer', 'public'}

def get_role():
    role = request.headers.get('X-User-Role', 'public').lower()
    return role if role in ROLES else 'public'

def require_role(*allowed_roles):
    """Abort 403 if current role not in allowed_roles."""
    if get_role() not in allowed_roles:
        abort(jsonify({'error': 'Forbidden — insufficient role', 'required': list(allowed_roles)}), 403)

# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad Request', 'message': str(e)}), 400

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# ── HTML Page Routes ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/traffic')
def traffic_page():
    return render_template('traffic.html')

@app.route('/incidents')
def incidents_page():
    return render_template('incidents.html')

@app.route('/observation')
def observation_page():
    return render_template('observation.html')

@app.route('/roads')
def roads_page():
    return render_template('roads_junctions.html')

# ── Health check ──────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Simple liveness probe."""
    try:
        db = get_db()
        db.execute("SELECT 1")
        return jsonify({'status': 'ok', 'db': DB_PATH}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ── ZONES ─────────────────────────────────────────────────────────────────────

@app.route('/api/zones', methods=['GET'])
def get_zones():
    db = get_db()
    rows = db.execute("SELECT * FROM Zone ORDER BY zone_name").fetchall()
    return jsonify(rows_to_list(rows)), 200

# ── ROADS ─────────────────────────────────────────────────────────────────────

@app.route('/api/roads', methods=['GET'])
def get_roads():
    """List all roads, optionally filtered by zone_id or road_type."""
    db    = get_db()
    zone  = request.args.get('zone_id', type=int)
    rtype = request.args.get('road_type')

    sql    = "SELECT r.*, z.zone_name FROM Road r JOIN Zone z ON r.zone_id = z.zone_id WHERE 1=1"
    params = []

    if zone:
        sql += " AND r.zone_id = ?"
        params.append(zone)
    if rtype:
        sql += " AND r.road_type = ?"
        params.append(rtype)

    sql += " ORDER BY r.road_name"
    rows = db.execute(sql, params).fetchall()
    return jsonify(rows_to_list(rows)), 200


@app.route('/api/roads/<int:road_id>', methods=['GET'])
def get_road(road_id):
    db  = get_db()
    row = db.execute(
        "SELECT r.*, z.zone_name FROM Road r JOIN Zone z ON r.zone_id = z.zone_id WHERE r.road_id = ?",
        (road_id,)
    ).fetchone()
    if row is None:
        abort(404)
    return jsonify(dict(row)), 200

# ── JUNCTIONS ─────────────────────────────────────────────────────────────────

@app.route('/api/junctions', methods=['GET'])
def get_junctions():
    db   = get_db()
    zone = request.args.get('zone_id', type=int)

    sql    = """
        SELECT j.*, z.zone_name
        FROM Junction j
        JOIN Zone z ON j.zone_id = z.zone_id
        WHERE 1=1
    """
    params = []
    if zone:
        sql += " AND j.zone_id = ?"
        params.append(zone)
    sql += " ORDER BY j.junction_name"

    rows = db.execute(sql, params).fetchall()
    return jsonify(rows_to_list(rows)), 200

# ── TRAFFIC OBSERVATIONS ──────────────────────────────────────────────────────

@app.route('/api/traffic', methods=['GET'])
def get_traffic():
    """
    Recent traffic observations.
    Optional filters: junction_id, road_id, congestion_level, hours (default 24).
    """
    db      = get_db()
    jid     = request.args.get('junction_id', type=int)
    rid     = request.args.get('road_id',     type=int)
    level   = request.args.get('congestion_level')
    hours   = request.args.get('hours', 24, type=int)
    limit   = min(request.args.get('limit', 100, type=int), 500)

    sql    = """
        SELECT t.*, j.junction_name, r.road_name, z.zone_name
        FROM Traffic_Observation t
        JOIN Junction j ON t.junction_id = j.junction_id
        JOIN Road     r ON t.road_id     = r.road_id
        JOIN Zone     z ON j.zone_id     = z.zone_id
        WHERE t.observation_time >= datetime('now', ?)
    """
    params = [f'-{hours} hours']

    if jid:
        sql += " AND t.junction_id = ?"
        params.append(jid)
    if rid:
        sql += " AND t.road_id = ?"
        params.append(rid)
    if level:
        sql += " AND t.congestion_level = ?"
        params.append(level.upper())

    sql += " ORDER BY t.observation_time DESC LIMIT ?"
    params.append(limit)

    rows = db.execute(sql, params).fetchall()
    return jsonify(rows_to_list(rows)), 200


@app.route('/api/traffic/<int:road_id>', methods=['GET'])
def get_traffic_by_road(road_id):
    """Latest 50 observations for a specific road."""
    db   = get_db()
    rows = db.execute(
        """
        SELECT t.*, j.junction_name, r.road_name
        FROM Traffic_Observation t
        JOIN Junction j ON t.junction_id = j.junction_id
        JOIN Road     r ON t.road_id     = r.road_id
        WHERE t.road_id = ?
        ORDER BY t.observation_time DESC
        LIMIT 50
        """,
        (road_id,)
    ).fetchall()
    return jsonify(rows_to_list(rows)), 200


@app.route('/api/traffic', methods=['POST'])
def post_traffic():
    """
    Insert a new traffic observation.
    Requires role: officer | admin
    Demonstrates: ACID Transaction T1 (INSERT + junction UPDATE in one atomic block)
    Two-Phase Locking: growing phase acquires locks on Traffic_Observation and Junction;
    shrinking phase releases all at COMMIT.
    """
    if get_role() not in ('officer', 'admin'):
        return jsonify({'error': 'Forbidden — officer or admin role required'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    required = ['junction_id', 'road_id', 'vehicle_count', 'avg_speed_kmph',
                'congestion_level', 'data_source']
    missing  = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'fields': missing}), 400

    # Validate enum values
    valid_levels   = {'LOW', 'MODERATE', 'HIGH', 'SEVERE'}
    valid_sources  = {'Sensor', 'Manual', 'Camera', 'API'}
    valid_weather  = {'Clear', 'Rainy', 'Foggy', 'Cloudy', 'Stormy', None}

    if data['congestion_level'].upper() not in valid_levels:
        return jsonify({'error': f"congestion_level must be one of {valid_levels}"}), 400
    if data['data_source'] not in valid_sources:
        return jsonify({'error': f"data_source must be one of {valid_sources}"}), 400
    if data.get('weather_condition') not in valid_weather:
        return jsonify({'error': f"weather_condition must be one of {valid_weather}"}), 400

    db = get_db()

    # Verify FK targets exist before transaction
    junc = db.execute("SELECT junction_id FROM Junction WHERE junction_id = ?",
                      (data['junction_id'],)).fetchone()
    road = db.execute("SELECT road_id FROM Road WHERE road_id = ?",
                      (data['road_id'],)).fetchone()
    if not junc:
        return jsonify({'error': f"junction_id {data['junction_id']} does not exist"}), 400
    if not road:
        return jsonify({'error': f"road_id {data['road_id']} does not exist"}), 400

    try:
        # ACID Transaction T1: INSERT observation + UPDATE junction congestion atomically
        # 2PL Growing phase: acquire write locks on both tables before any write
        db.execute("BEGIN")
        cursor = db.execute(
            """
            INSERT INTO Traffic_Observation
                (junction_id, road_id, observation_time, vehicle_count,
                 avg_speed_kmph, congestion_level, weather_condition, data_source)
            VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?)
            """,
            (
                data['junction_id'],
                data['road_id'],
                int(data['vehicle_count']),
                float(data['avg_speed_kmph']),
                data['congestion_level'].upper(),
                data.get('weather_condition'),
                data['data_source']
            )
        )
        obs_id = cursor.lastrowid

        # Update junction congestion status (mirrors trigger trg_congestion_alert/clear)
        vehicle_count = int(data['vehicle_count'])
        if vehicle_count > 200:
            new_status = 'HIGH'
        elif vehicle_count < 100:
            new_status = 'NORMAL'
        else:
            new_status = None   # leave unchanged

        if new_status:
            db.execute(
                "UPDATE Junction SET congestion_status = ? WHERE junction_id = ?",
                (new_status, data['junction_id'])
            )

        # 2PL Shrinking phase: COMMIT releases all locks
        db.execute("COMMIT")
        return jsonify({'message': 'Observation recorded', 'obs_id': obs_id}), 201

    except sqlite3.IntegrityError as e:
        db.execute("ROLLBACK")
        return jsonify({'error': 'Integrity constraint violation', 'detail': str(e)}), 400
    except Exception as e:
        db.execute("ROLLBACK")
        return jsonify({'error': 'Transaction failed', 'detail': str(e)}), 500

# ── INCIDENTS ─────────────────────────────────────────────────────────────────

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """
    List incidents.
    Optional filters: severity, road_id, open_only (default true), zone_id.
    """
    db        = get_db()
    severity  = request.args.get('severity')
    road_id   = request.args.get('road_id',   type=int)
    zone_id   = request.args.get('zone_id',   type=int)
    open_only = request.args.get('open_only', 'true').lower() == 'true'
    limit     = min(request.args.get('limit', 50, type=int), 200)

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
    params = []

    if open_only:
        sql += " AND i.resolved_datetime IS NULL"
    if severity:
        sql += " AND i.severity = ?"
        params.append(severity.upper())
    if road_id:
        sql += " AND i.road_id = ?"
        params.append(road_id)
    if zone_id:
        sql += " AND (rz.zone_id = ? OR jz.zone_id = ?)"
        params += [zone_id, zone_id]

    sql += " ORDER BY CASE i.severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, i.reported_datetime DESC LIMIT ?"
    params.append(limit)

    rows = db.execute(sql, params).fetchall()
    return jsonify(rows_to_list(rows)), 200


@app.route('/api/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    db  = get_db()
    row = db.execute(
        """
        SELECT i.*, r.road_name, j.junction_name,
               COALESCE(rz.zone_name, jz.zone_name) AS zone_name,
               v.license_plate, v.vehicle_type
        FROM Incident i
        LEFT JOIN Road     r  ON i.road_id     = r.road_id
        LEFT JOIN Zone     rz ON r.zone_id     = rz.zone_id
        LEFT JOIN Junction j  ON i.junction_id = j.junction_id
        LEFT JOIN Zone     jz ON j.zone_id     = jz.zone_id
        LEFT JOIN Vehicle  v  ON i.vehicle_id  = v.vehicle_id
        WHERE i.incident_id = ?
        """,
        (incident_id,)
    ).fetchone()
    if row is None:
        abort(404)
    return jsonify(dict(row)), 200


@app.route('/api/incidents', methods=['POST'])
def post_incident():
    """
    Report a new incident. Requires role: officer | admin.
    """
    if get_role() not in ('officer', 'admin'):
        return jsonify({'error': 'Forbidden — officer or admin role required'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    required = ['incident_type', 'severity']
    missing  = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'fields': missing}), 400

    valid_types      = {'Accident', 'Breakdown', 'Roadblock', 'Flooding'}
    valid_severities = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}

    if data['incident_type'] not in valid_types:
        return jsonify({'error': f"incident_type must be one of {valid_types}"}), 400
    if data['severity'].upper() not in valid_severities:
        return jsonify({'error': f"severity must be one of {valid_severities}"}), 400

    db = get_db()
    try:
        db.execute("BEGIN")
        cursor = db.execute(
            """
            INSERT INTO Incident
                (incident_type, severity, description,
                 reported_datetime, road_id, junction_id, vehicle_id, reported_by)
            VALUES (?, ?, ?, datetime('now'), ?, ?, ?, ?)
            """,
            (
                data['incident_type'],
                data['severity'].upper(),
                data.get('description'),
                data.get('road_id'),
                data.get('junction_id'),
                data.get('vehicle_id'),
                data.get('reported_by', 'API')
            )
        )
        inc_id = cursor.lastrowid
        db.execute("COMMIT")
        return jsonify({'message': 'Incident reported', 'incident_id': inc_id}), 201

    except sqlite3.IntegrityError as e:
        db.execute("ROLLBACK")
        return jsonify({'error': 'Integrity constraint violation', 'detail': str(e)}), 400
    except Exception as e:
        db.execute("ROLLBACK")
        return jsonify({'error': 'Transaction failed', 'detail': str(e)}), 500


@app.route('/api/incidents/<int:incident_id>', methods=['PUT'])
def update_incident(incident_id):
    """
    Update (resolve) an incident. Requires role: officer | admin.
    Demonstrates: ACID Transaction T2 — consistency check via changes() = 1.
    Trigger trg_validate_resolution_time enforces resolved >= reported at DB layer.
    """
    if get_role() not in ('officer', 'admin'):
        return jsonify({'error': 'Forbidden — officer or admin role required'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    db  = get_db()
    row = db.execute("SELECT * FROM Incident WHERE incident_id = ?", (incident_id,)).fetchone()
    if row is None:
        abort(404)

    # Build SET clause dynamically — only update fields provided
    allowed_fields = {'severity', 'description', 'resolved_datetime', 'reported_by'}
    updates        = {k: v for k, v in data.items() if k in allowed_fields}

    if 'resolved_datetime' in updates and updates['resolved_datetime'] == 'now':
        updates['resolved_datetime'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if not updates:
        return jsonify({'error': 'No updatable fields provided'}), 400

    # Validate resolved_datetime > reported_datetime at application layer
    # (trigger trg_validate_resolution_time also enforces this at DB layer)
    if 'resolved_datetime' in updates and updates['resolved_datetime']:
        try:
            res_dt  = datetime.fromisoformat(updates['resolved_datetime'])
            rep_dt  = datetime.fromisoformat(str(row['reported_datetime']))
            if res_dt < rep_dt:
                return jsonify({'error': 'resolved_datetime cannot be before reported_datetime'}), 400
        except ValueError:
            return jsonify({'error': 'resolved_datetime must be ISO 8601 format (YYYY-MM-DD HH:MM:SS)'}), 400

    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values     = list(updates.values()) + [incident_id]

    try:
        db.execute("BEGIN")
        db.execute(f"UPDATE Incident SET {set_clause} WHERE incident_id = ?", values)
        # CONSISTENCY check: exactly 1 row must have been updated
        changed = db.execute("SELECT changes()").fetchone()[0]
        if changed != 1:
            db.execute("ROLLBACK")
            return jsonify({'error': 'Update affected unexpected number of rows', 'rows': changed}), 500
        db.execute("COMMIT")
        return jsonify({'message': 'Incident updated', 'incident_id': incident_id}), 200

    except sqlite3.IntegrityError as e:
        db.execute("ROLLBACK")
        return jsonify({'error': 'Constraint violation', 'detail': str(e)}), 400
    except Exception as e:
        db.execute("ROLLBACK")
        return jsonify({'error': 'Transaction failed', 'detail': str(e)}), 500


@app.route('/api/incidents/<int:incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """
    Delete an incident. Requires role: admin only.
    Demonstrates RBAC: DELETE is admin-only; officers cannot delete.
    """
    if get_role() != 'admin':
        return jsonify({'error': 'Forbidden — admin role required for DELETE'}), 403

    db  = get_db()
    row = db.execute("SELECT incident_id FROM Incident WHERE incident_id = ?", (incident_id,)).fetchone()
    if row is None:
        abort(404)

    db.execute("DELETE FROM Incident WHERE incident_id = ?", (incident_id,))
    db.commit()
    return jsonify({'message': 'Incident deleted', 'incident_id': incident_id}), 200

# ── MAP DATA ──────────────────────────────────────────────────────────────────

@app.route('/api/map', methods=['GET'])
def get_map_data():
    """
    Returns all data needed to render the Leaflet.js map:
      - junctions with lat/lon + most-recent congestion level + vehicle count
      - open incidents with coordinates (from junction or road's first junction)
    """
    db = get_db()

    # Junctions: most recent observation congestion per junction
    junctions = db.execute(
        """
        SELECT
            j.junction_id,
            j.junction_name,
            j.latitude,
            j.longitude,
            j.junction_type,
            j.congestion_status,
            z.zone_name,
            t.congestion_level,
            t.vehicle_count,
            t.avg_speed_kmph,
            t.observation_time,
            t.weather_condition,
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
        """
    ).fetchall()

    # Open incidents: join to junction coords where available
    incidents = db.execute(
        """
        SELECT
            i.incident_id,
            i.incident_type,
            i.severity,
            i.description,
            i.reported_datetime,
            r.road_name,
            j.junction_name,
            j.latitude,
            j.longitude
        FROM Incident i
        LEFT JOIN Junction j ON i.junction_id = j.junction_id
        LEFT JOIN Road r     ON i.road_id     = r.road_id
        WHERE i.resolved_datetime IS NULL
          AND j.latitude IS NOT NULL
          AND j.longitude IS NOT NULL
        ORDER BY CASE i.severity
            WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM'   THEN 3 ELSE 4 END
        """
    ).fetchall()

    return jsonify({
        'junctions': rows_to_list(junctions),
        'incidents':  rows_to_list(incidents)
    }), 200

# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """
    Aggregate dashboard data: uses TrafficDashboard and ZoneSummary views.
    Returns: most-recent observation per junction + zone summary.
    Public access allowed (no PII exposed).
    """
    db = get_db()

    # TrafficDashboard view — most recent observation per junction
    junctions = db.execute("SELECT * FROM TrafficDashboard ORDER BY congestion_level DESC NULLS LAST").fetchall()

    # ZoneSummary view — aggregated zone stats
    zones = db.execute("SELECT * FROM ZoneSummary ORDER BY open_incidents DESC").fetchall()

    # City-level KPIs (Q4 pattern)
    kpis = db.execute(
        """
        SELECT
            COUNT(*) AS total_observations_24h,
            ROUND(AVG(vehicle_count), 0) AS city_avg_vehicles,
            ROUND(AVG(avg_speed_kmph), 1) AS city_avg_speed,
            SUM(CASE WHEN congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END) AS high_congestion_count
        FROM Traffic_Observation
        WHERE observation_time >= datetime('now', '-1 day')
        """
    ).fetchone()

    # Open incidents count by severity
    incident_summary = db.execute(
        """
        SELECT severity, COUNT(*) AS count
        FROM Incident
        WHERE resolved_datetime IS NULL
        GROUP BY severity
        ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END
        """
    ).fetchall()

    return jsonify({
        'junctions':        rows_to_list(junctions),
        'zones':            rows_to_list(zones),
        'city_kpis':        dict(kpis) if kpis else {},
        'incident_summary': rows_to_list(incident_summary)
    }), 200

# ── ANALYTICS ─────────────────────────────────────────────────────────────────

@app.route('/api/analytics/peak-hours', methods=['GET'])
def peak_hours():
    """Q21: Peak congestion hours across all junctions."""
    db   = get_db()
    rows = db.execute(
        """
        SELECT
            strftime('%H', observation_time) AS hour_of_day,
            COUNT(*) AS total_observations,
            ROUND(AVG(vehicle_count), 0) AS avg_vehicles,
            SUM(CASE WHEN congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END) AS high_congestion_obs
        FROM Traffic_Observation
        GROUP BY hour_of_day
        ORDER BY avg_vehicles DESC
        """
    ).fetchall()
    return jsonify(rows_to_list(rows)), 200


@app.route('/api/analytics/zone-summary', methods=['GET'])
def zone_summary():
    """ZoneSummary view — city planner view."""
    db   = get_db()
    rows = db.execute("SELECT * FROM ZoneSummary ORDER BY zone_name").fetchall()
    return jsonify(rows_to_list(rows)), 200


@app.route('/api/analytics/top-congested', methods=['GET'])
def top_congested():
    """Q7: Top 5 most congested junctions in last 24 hours."""
    db   = get_db()
    rows = db.execute(
        """
        SELECT j.junction_name, z.zone_name,
               COUNT(t.obs_id) AS obs_count,
               ROUND(AVG(t.vehicle_count), 0) AS avg_vehicles,
               ROUND(AVG(t.avg_speed_kmph), 1) AS avg_speed
        FROM Traffic_Observation t
        INNER JOIN Junction j ON t.junction_id = j.junction_id
        INNER JOIN Zone     z ON j.zone_id     = z.zone_id
        WHERE t.observation_time >= datetime('now', '-1 day')
        GROUP BY j.junction_id, j.junction_name, z.zone_name
        ORDER BY avg_vehicles DESC
        LIMIT 5
        """
    ).fetchall()
    return jsonify(rows_to_list(rows)), 200

# ── AUDIT LOG (admin only) ────────────────────────────────────────────────────

@app.route('/api/audit', methods=['GET'])
def get_audit_log():
    """Return incident audit trail. Admin only."""
    if get_role() != 'admin':
        return jsonify({'error': 'Forbidden — admin role required'}), 403
    db   = get_db()
    rows = db.execute(
        "SELECT * FROM Incident_Audit ORDER BY changed_at DESC LIMIT 100"
    ).fetchall()
    return jsonify(rows_to_list(rows)), 200

# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(os.path.join(BASE_DIR, '..', 'data'), exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
