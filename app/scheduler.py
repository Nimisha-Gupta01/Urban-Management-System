"""
app/scheduler.py
APScheduler background jobs for the Urban Traffic Management System.

Jobs:
  1. decay_congestion   — every 60s: reset stale junctions to NORMAL
  2. signal_rule_engine — every 60s: extend green phase on congested junctions
  3. aggregate_sensors  — every 60s: aggregate Sensor_Reading -> Traffic_Observation
  4. severe_alerts      — every 5min: email alert if junction SEVERE > 15 min
"""

import os
import logging
import psycopg2
import psycopg2.extras
from apscheduler.schedulers.background import BackgroundScheduler

log = logging.getLogger(__name__)

DB_CONFIG = {
    "host":     os.getenv("PGHOST",     "localhost"),
    "port":     int(os.getenv("PGPORT", "5432")),
    "dbname":   os.getenv("PGDATABASE", "traffic_db"),
    "user":     os.getenv("PGUSER",     "traffic_user"),
    "password": os.getenv("PGPASSWORD", "traffic_pass"),
}

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
ALERT_EMAIL      = os.getenv("ALERT_EMAIL", "")


def _get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn


def decay_congestion():
    """Reset junction congestion_status to NORMAL if no observation in last 10 min."""
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Junction
                SET congestion_status = 'NORMAL'
                WHERE congestion_status = 'HIGH'
                  AND junction_id NOT IN (
                      SELECT DISTINCT junction_id
                      FROM Traffic_Observation
                      WHERE observation_time >= NOW() - INTERVAL '10 minutes'
                  )
            """)
            if cur.rowcount > 0:
                log.info(f"[decay] Reset {cur.rowcount} stale junction(s) to NORMAL")
        conn.close()
    except Exception as e:
        log.error(f"[decay] Error: {e}")


def signal_rule_engine():
    """Extend green phase for signals at HIGH junctions (max 120s). Reset on NORMAL."""
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Traffic_Signal ts
                SET green_duration_sec = LEAST(ts.green_duration_sec + 30, 120)
                FROM Junction j
                WHERE ts.junction_id = j.junction_id
                  AND ts.operational_status = 'Active'
                  AND j.congestion_status = 'HIGH'
                  AND ts.green_duration_sec < 120
            """)
            extended = cur.rowcount

            cur.execute("""
                UPDATE Traffic_Signal ts
                SET green_duration_sec = 30
                FROM Junction j
                WHERE ts.junction_id = j.junction_id
                  AND ts.operational_status = 'Active'
                  AND j.congestion_status = 'NORMAL'
                  AND ts.green_duration_sec > 30
            """)
            reset = cur.rowcount

            if extended or reset:
                log.info(f"[signals] Extended {extended} signal(s), reset {reset} signal(s)")
        conn.close()
    except Exception as e:
        log.error(f"[signals] Error: {e}")


def aggregate_sensors():
    """Aggregate Sensor_Reading rows into Traffic_Observation every 60s."""
    try:
        conn = _get_conn()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'sensor_reading'
                )
            """)
            if not cur.fetchone()["exists"]:
                conn.close()
                return

            cur.execute("""
                SELECT sr.sensor_id, s.junction_id,
                       ROUND(AVG(sr.vehicle_count)) AS avg_count,
                       ROUND(AVG(sr.avg_speed)::NUMERIC, 1) AS avg_speed
                FROM Sensor_Reading sr
                JOIN Sensor s ON sr.sensor_id = s.sensor_id
                WHERE sr.read_time >= NOW() - INTERVAL '2 minutes'
                GROUP BY sr.sensor_id, s.junction_id
            """)
            readings = cur.fetchall()

            for r in readings:
                junction_id = r["junction_id"]
                avg_count   = int(r["avg_count"] or 0)
                avg_speed   = float(r["avg_speed"] or 0)

                if avg_count >= 200:
                    level = "SEVERE"
                elif avg_count >= 120:
                    level = "HIGH"
                elif avg_count >= 60:
                    level = "MODERATE"
                else:
                    level = "LOW"

                cur.execute("""
                    SELECT road_id FROM Road_Junction
                    WHERE junction_id = %s LIMIT 1
                """, (junction_id,))
                road_row = cur.fetchone()
                if not road_row:
                    continue

                cur.execute("""
                    INSERT INTO Traffic_Observation
                        (junction_id, road_id, vehicle_count, avg_speed_kmph,
                         congestion_level, data_source, observation_time)
                    VALUES (%s, %s, %s, %s, %s, 'Sensor', NOW())
                """, (junction_id, road_row["road_id"],
                      avg_count, avg_speed, level))

            if readings:
                log.info(f"[aggregate] Aggregated {len(readings)} sensor(s) into observations")
        conn.close()
    except Exception as e:
        log.error(f"[aggregate] Error: {e}")


def severe_alerts():
    """Send email alert if a junction stays HIGH/SEVERE for 15+ minutes."""
    if not SENDGRID_API_KEY or not ALERT_EMAIL:
        return

    try:
        conn = _get_conn()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT j.junction_id, j.junction_name, z.zone_name,
                       COUNT(t.obs_id) AS obs_count,
                       MAX(t.vehicle_count) AS max_vehicles
                FROM Junction j
                JOIN Zone z ON j.zone_id = z.zone_id
                JOIN Traffic_Observation t ON j.junction_id = t.junction_id
                WHERE t.observation_time >= NOW() - INTERVAL '15 minutes'
                  AND t.congestion_level IN ('HIGH', 'SEVERE')
                GROUP BY j.junction_id, j.junction_name, z.zone_name
                HAVING COUNT(t.obs_id) >= 3
                   AND COUNT(t.obs_id) = SUM(
                       CASE WHEN t.congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END
                   )
            """)
            severe_junctions = cur.fetchall()
        conn.close()

        if not severe_junctions:
            return

        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        for j in severe_junctions:
            body = (
                f"ALERT: {j['junction_name']} ({j['zone_name']}) has been "
                f"severely congested for 15+ minutes. "
                f"Max vehicles: {j['max_vehicles']}. "
                f"Observations in window: {j['obs_count']}."
            )
            message = Mail(
                from_email="alerts@utms.local",
                to_emails=ALERT_EMAIL,
                subject=f"Traffic Alert: {j['junction_name']} SEVERE congestion",
                plain_text_content=body,
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            log.info(f"[alerts] Sent alert for {j['junction_name']}")

    except Exception as e:
        log.error(f"[alerts] Error: {e}")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(decay_congestion,   "interval", seconds=60,  id="decay")
    scheduler.add_job(signal_rule_engine, "interval", seconds=60,  id="signals")
    scheduler.add_job(aggregate_sensors,  "interval", seconds=60,  id="aggregate")
    scheduler.add_job(severe_alerts,      "interval", seconds=300, id="alerts")
    scheduler.start()
    log.info("APScheduler started with 4 jobs.")
    return scheduler
