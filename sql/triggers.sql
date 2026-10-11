-- ============================================================
-- Urban Road & Real-Time Traffic Management System
-- BITS Pilani WILP | SESAP ZC337
-- triggers.sql — Triggers, Views, Transactions, Security, Recovery
-- DBSA Concepts: Triggers (PL/pgSQL), SQL Views, ACID Transactions,
--   Two-Phase Locking (2PL), WAL Recovery, Access Control (GRANT/REVOKE)
-- ============================================================

-- ============================================================
-- VIEWS (External Schema — Three-Schema Architecture)
-- ============================================================

-- View 1: Real-time traffic dashboard (most recent observation per junction)
CREATE OR REPLACE VIEW TrafficDashboard AS
SELECT
    j.junction_id,
    j.junction_name,
    j.junction_type,
    j.congestion_status,
    z.zone_name,
    t.observation_time,
    t.vehicle_count,
    t.avg_speed_kmph,
    t.congestion_level,
    t.weather_condition,
    t.data_source,
    ts.operational_status AS signal_status
FROM Junction j
INNER JOIN Zone z ON j.zone_id = z.zone_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
    AND t.observation_time = (
        SELECT MAX(t2.observation_time)
        FROM Traffic_Observation t2
        WHERE t2.junction_id = j.junction_id
    )
LEFT JOIN Traffic_Signal ts ON j.junction_id = ts.junction_id
    AND ts.operational_status = 'Active';

-- View 2: Zone congestion summary (for city planners)
CREATE OR REPLACE VIEW ZoneSummary AS
SELECT
    z.zone_id,
    z.zone_name,
    z.zone_type,
    COUNT(DISTINCT j.junction_id) AS total_junctions,
    COUNT(DISTINCT r.road_id) AS total_roads,
    COUNT(t.obs_id) AS observations_last_24h,
    ROUND(AVG(t.vehicle_count)::NUMERIC, 0) AS avg_vehicle_count,
    ROUND(AVG(t.avg_speed_kmph)::NUMERIC, 1) AS avg_speed_kmph,
    SUM(CASE WHEN i.resolved_datetime IS NULL THEN 1 ELSE 0 END) AS open_incidents
FROM Zone z
LEFT JOIN Junction j ON z.zone_id = j.zone_id
LEFT JOIN Road r ON z.zone_id = r.zone_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
    AND t.observation_time >= NOW() - INTERVAL '1 day'
LEFT JOIN Incident i ON r.road_id = i.road_id
GROUP BY z.zone_id, z.zone_name, z.zone_type;

-- View 3: Open incident report with full context
CREATE OR REPLACE VIEW OpenIncidentReport AS
SELECT
    i.incident_id,
    i.incident_type,
    i.severity,
    i.description,
    i.reported_datetime,
    TO_CHAR(i.reported_datetime, 'HH24:MI') AS reported_time,
    EXTRACT(EPOCH FROM (NOW() - i.reported_datetime)) / 3600 AS hours_open,
    r.road_name,
    j.junction_name,
    z.zone_name,
    v.license_plate AS vehicle_plate,
    i.reported_by
FROM Incident i
LEFT JOIN Road r ON i.road_id = r.road_id
LEFT JOIN Junction j ON i.junction_id = j.junction_id
LEFT JOIN Zone z ON COALESCE(r.zone_id, j.zone_id) = z.zone_id
LEFT JOIN Vehicle v ON i.vehicle_id = v.vehicle_id
WHERE i.resolved_datetime IS NULL
ORDER BY
    CASE i.severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH'     THEN 2
        WHEN 'MEDIUM'   THEN 3
        WHEN 'LOW'      THEN 4
    END,
    i.reported_datetime ASC;

-- View 4: Public-facing view (restricted data — no vehicle/driver PII)
CREATE OR REPLACE VIEW PublicTrafficView AS
SELECT
    j.junction_name,
    z.zone_name,
    t.observation_time,
    t.congestion_level,
    t.vehicle_count,
    t.avg_speed_kmph,
    t.weather_condition
FROM Traffic_Observation t
INNER JOIN Junction j ON t.junction_id = j.junction_id
INNER JOIN Zone z ON j.zone_id = z.zone_id
WHERE t.observation_time >= NOW() - INTERVAL '1 hour'
ORDER BY t.observation_time DESC;

-- ============================================================
-- TRIGGER FUNCTIONS (PL/pgSQL)
-- DBSA Concept: Active Database — triggers enforce business rules
-- ============================================================

-- Trigger 1: Auto-flag junction as HIGH congestion when vehicle_count > 200
CREATE OR REPLACE FUNCTION fn_congestion_alert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.vehicle_count > 200 THEN
        UPDATE Junction
        SET congestion_status = 'HIGH'
        WHERE junction_id = NEW.junction_id;
    ELSIF NEW.vehicle_count < 100 THEN
        UPDATE Junction
        SET congestion_status = 'NORMAL'
        WHERE junction_id = NEW.junction_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_congestion_alert ON Traffic_Observation;
CREATE TRIGGER trg_congestion_alert
AFTER INSERT ON Traffic_Observation
FOR EACH ROW EXECUTE FUNCTION fn_congestion_alert();

-- Trigger 2: Prevent resolving an incident with resolved_datetime before reported_datetime
CREATE OR REPLACE FUNCTION fn_validate_resolution_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.resolved_datetime IS NOT NULL
       AND NEW.resolved_datetime < NEW.reported_datetime THEN
        RAISE EXCEPTION 'resolved_datetime cannot be before reported_datetime';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_resolution_time ON Incident;
CREATE TRIGGER trg_validate_resolution_time
BEFORE UPDATE OF resolved_datetime ON Incident
FOR EACH ROW EXECUTE FUNCTION fn_validate_resolution_time();

-- Trigger 3: Log incident updates to audit table
CREATE OR REPLACE FUNCTION fn_audit_incident_update()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Incident_Audit(incident_id, action, old_severity, new_severity, changed_at)
    VALUES (NEW.incident_id, 'UPDATE', OLD.severity, NEW.severity, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_incident_update ON Incident;
CREATE TRIGGER trg_audit_incident_update
AFTER UPDATE ON Incident
FOR EACH ROW EXECUTE FUNCTION fn_audit_incident_update();

-- ============================================================
-- TRANSACTIONS — ACID DEMONSTRATION
-- DBSA Concepts: Atomicity, Consistency, Isolation, Durability
-- Two-Phase Locking (2PL) protocol
-- ============================================================

-- Transaction T1: Atomic observation insert + junction update
-- Demonstrates ATOMICITY: both succeed or both rollback
-- 2PL Growing phase: acquire locks on Traffic_Observation, Junction
-- 2PL Shrinking phase: release all locks at COMMIT
BEGIN;
    INSERT INTO Traffic_Observation(junction_id, road_id, observation_time,
        vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source)
    VALUES (1, 1, NOW(), 250, 18.5, 'SEVERE', 'Clear', 'Sensor');

    UPDATE Junction
    SET congestion_status = 'HIGH'
    WHERE junction_id = 1;
COMMIT;
-- If any statement fails -> ROLLBACK ensures atomicity
-- PostgreSQL WAL (Write-Ahead Logging) ensures DURABILITY — committed data survives crash

-- Transaction T2: Safe incident resolution (update + audit)
-- Demonstrates CONSISTENCY: FK constraints enforced throughout transaction
BEGIN;
    UPDATE Incident
    SET resolved_datetime = NOW(),
        description = description || ' | Resolved by Traffic Control Room'
    WHERE incident_id = 1
      AND resolved_datetime IS NULL;
    -- Application layer checks rowcount = 1 before committing
COMMIT;

-- Transaction T3: ROLLBACK demonstration (simulated failure)
BEGIN;
    INSERT INTO Traffic_Observation(junction_id, road_id, observation_time,
        vehicle_count, avg_speed_kmph, congestion_level, data_source)
    VALUES (999, 999, NOW(), 100, 40.0, 'LOW', 'Manual');
    -- Above will fail FK check (junction_id=999 does not exist)
ROLLBACK;
-- Result: no partial data inserted — atomicity preserved

-- ============================================================
-- CONCURRENCY CONTROL — 2PL DEMONSTRATION
-- DBSA Concept: Lock-based protocol, deadlock prevention
-- PostgreSQL uses MVCC (Multi-Version Concurrency Control) by default.
-- Serializable isolation level enforces strict 2PL behaviour.
-- ============================================================

-- To demonstrate serializable isolation:
-- BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
--   UPDATE Junction SET congestion_status = 'HIGH' WHERE junction_id = 1;
--   INSERT INTO Traffic_Observation ...;
-- COMMIT;

-- ============================================================
-- RECOVERY — WAL (Write-Ahead Log) Demonstration
-- DBSA Concepts: WAL, Checkpointing, UNDO/REDO
-- ============================================================

-- PostgreSQL WAL Mode Recovery Steps:
-- 1. All changes written to WAL (pg_wal/) before applied to heap files
-- 2. On crash mid-transaction:
--    - Committed transactions: replayed from WAL into data files (REDO)
--    - Uncommitted transactions: not in WAL -> effectively undone (UNDO)
-- 3. Checkpoint: dirty pages flushed from buffer pool to disk
-- 4. pg_walwriter background process manages WAL flushing

-- Manual checkpoint (run after bulk inserts for performance):
CHECKPOINT;

-- ============================================================
-- SECURITY — Access Control
-- DBSA Concept: Role-based access control, GRANT/REVOKE
-- PostgreSQL native roles (defined in schema.sql)
-- ============================================================

-- Role definitions (see schema.sql for GRANT/REVOKE statements):
-- admin_role: Full access (DDL + DML)
-- officer_role: SELECT all + INSERT/UPDATE on Traffic_Observation and Incident
-- public_role: SELECT on Zone, Road, Junction, Traffic_Observation only

-- Application-layer enforcement (FastAPI):
-- Each endpoint reads X-User-Role header (simulates session-based auth)
-- DELETE endpoints: admin only
-- POST endpoints: officer or admin
-- GET endpoints: public allowed; /api/vehicles and /api/drivers require auth
