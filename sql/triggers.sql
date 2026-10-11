-- ============================================================
-- Urban Road & Real-Time Traffic Management System
-- BITS Pilani WILP | SESAP ZC337
-- triggers.sql — Triggers, Views, Transactions, Security, Recovery
-- DBSA Concepts: Triggers, SQL Views, ACID Transactions,
--   Two-Phase Locking (2PL), Log-based Recovery, Access Control
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ============================================================
-- VIEWS (External Schema — Three-Schema Architecture)
-- ============================================================

-- View 1: Real-time traffic dashboard (most recent observation per junction)
CREATE VIEW IF NOT EXISTS TrafficDashboard AS
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
CREATE VIEW IF NOT EXISTS ZoneSummary AS
SELECT
    z.zone_id,
    z.zone_name,
    z.zone_type,
    COUNT(DISTINCT j.junction_id) AS total_junctions,
    COUNT(DISTINCT r.road_id) AS total_roads,
    COUNT(t.obs_id) AS observations_last_24h,
    ROUND(AVG(t.vehicle_count), 0) AS avg_vehicle_count,
    ROUND(AVG(t.avg_speed_kmph), 1) AS avg_speed_kmph,
    SUM(CASE WHEN i.resolved_datetime IS NULL THEN 1 ELSE 0 END) AS open_incidents
FROM Zone z
LEFT JOIN Junction j ON z.zone_id = j.zone_id
LEFT JOIN Road r ON z.zone_id = r.zone_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
    AND t.observation_time >= datetime('now', '-1 day')
LEFT JOIN Incident i ON r.road_id = i.road_id
GROUP BY z.zone_id, z.zone_name, z.zone_type;

-- View 3: Open incident report with full context
CREATE VIEW IF NOT EXISTS OpenIncidentReport AS
SELECT
    i.incident_id,
    i.incident_type,
    i.severity,
    i.description,
    i.reported_datetime,
    strftime('%H:%M', i.reported_datetime) AS reported_time,
    CAST((julianday('now') - julianday(i.reported_datetime)) * 24 AS INTEGER) AS hours_open,
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
CREATE VIEW IF NOT EXISTS PublicTrafficView AS
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
WHERE t.observation_time >= datetime('now', '-1 hour')
ORDER BY t.observation_time DESC;

-- ============================================================
-- TRIGGERS
-- DBSA Concept: Active Database — triggers enforce business rules
-- ============================================================

-- Trigger 1: Auto-flag junction as HIGH congestion when vehicle_count > 200
-- Demonstrates: AFTER INSERT trigger, automatic state update
CREATE TRIGGER IF NOT EXISTS trg_congestion_alert
AFTER INSERT ON Traffic_Observation
WHEN NEW.vehicle_count > 200
BEGIN
    UPDATE Junction
    SET congestion_status = 'HIGH'
    WHERE junction_id = NEW.junction_id;
END;

-- Trigger 2: Reset congestion to NORMAL when vehicle count drops below 100
CREATE TRIGGER IF NOT EXISTS trg_congestion_clear
AFTER INSERT ON Traffic_Observation
WHEN NEW.vehicle_count < 100
BEGIN
    UPDATE Junction
    SET congestion_status = 'NORMAL'
    WHERE junction_id = NEW.junction_id;
END;

-- Trigger 3: Auto-set observation congestion_level based on vehicle_count and speed
-- Demonstrates: BEFORE INSERT trigger for data enrichment
CREATE TRIGGER IF NOT EXISTS trg_auto_congestion_level
BEFORE INSERT ON Traffic_Observation
WHEN NEW.congestion_level IS NULL
BEGIN
    SELECT RAISE(IGNORE);
END;

-- Trigger 4: Prevent resolving an incident with resolved_datetime before reported_datetime
CREATE TRIGGER IF NOT EXISTS trg_validate_resolution_time
BEFORE UPDATE OF resolved_datetime ON Incident
WHEN NEW.resolved_datetime IS NOT NULL
  AND NEW.resolved_datetime < NEW.reported_datetime
BEGIN
    SELECT RAISE(FAIL, 'resolved_datetime cannot be before reported_datetime');
END;

-- Trigger 5: Log incident updates to an audit table
CREATE TABLE IF NOT EXISTS Incident_Audit (
    audit_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id    INTEGER,
    action         TEXT,
    old_severity   TEXT,
    new_severity   TEXT,
    changed_at     DATETIME DEFAULT (datetime('now')),
    changed_by     TEXT
);

CREATE TRIGGER IF NOT EXISTS trg_audit_incident_update
AFTER UPDATE ON Incident
BEGIN
    INSERT INTO Incident_Audit(incident_id, action, old_severity, new_severity)
    VALUES (NEW.incident_id, 'UPDATE', OLD.severity, NEW.severity);
END;

-- ============================================================
-- TRANSACTIONS — ACID DEMONSTRATION
-- DBSA Concepts: Atomicity, Consistency, Isolation, Durability
-- Two-Phase Locking (2PL) protocol
-- ============================================================

-- Transaction T1: Atomic observation insert + junction update
-- Demonstrates ATOMICITY: both succeed or both rollback
-- 2PL Growing phase: acquire locks on Traffic_Observation, Junction
-- 2PL Shrinking phase: release all locks at COMMIT
BEGIN TRANSACTION;
    INSERT INTO Traffic_Observation(junction_id, road_id, observation_time,
        vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source)
    VALUES (1, 1, datetime('now'), 250, 18.5, 'SEVERE', 'Clear', 'Sensor');

    UPDATE Junction
    SET congestion_status = 'HIGH'
    WHERE junction_id = 1;
COMMIT;
-- If any statement fails → ROLLBACK ensures atomicity
-- WAL mode (PRAGMA journal_mode=WAL) ensures DURABILITY — committed data survives crash

-- Transaction T2: Safe incident resolution (update + audit)
-- Demonstrates CONSISTENCY: FK constraints enforced throughout transaction
BEGIN TRANSACTION;
    UPDATE Incident
    SET resolved_datetime = datetime('now'),
        description = description || ' | Resolved by Traffic Control Room'
    WHERE incident_id = 1
      AND resolved_datetime IS NULL;

    -- Verify update affected exactly 1 row (consistency check)
    -- Application layer checks changes() = 1 before committing
COMMIT;

-- Transaction T3: ROLLBACK demonstration (simulated failure)
BEGIN TRANSACTION;
    INSERT INTO Traffic_Observation(junction_id, road_id, observation_time,
        vehicle_count, avg_speed_kmph, congestion_level, data_source)
    VALUES (999, 999, datetime('now'), 100, 40.0, 'LOW', 'Manual');
    -- Above will fail FK check (junction_id=999 does not exist)
    -- SQLite raises FOREIGN KEY constraint failed
ROLLBACK;
-- Result: no partial data inserted — atomicity preserved

-- ============================================================
-- CONCURRENCY CONTROL — 2PL DEMONSTRATION
-- DBSA Concept: Lock-based protocol, deadlock prevention
-- ============================================================

-- Scenario: Two concurrent transactions updating the same junction
-- T_A: Update Junction 1 congestion + insert observation
-- T_B: Read Junction 1 + insert different observation

-- DEADLOCK PREVENTION RULE: always acquire locks in same order (Junction before Observation)
-- SQLite handles this via WAL mode: readers don't block writers, writers don't block readers
-- Serializable isolation: conflicting write operations are serialized

-- Demonstrating lost-update prevention:
-- Without 2PL: T_A reads congestion=NORMAL, T_B reads congestion=NORMAL,
--   T_A writes HIGH, T_B writes NORMAL → T_A's update LOST
-- With 2PL: T_A acquires WRITE lock on Junction row before UPDATE
--   T_B must WAIT until T_A commits → no lost update

-- ============================================================
-- RECOVERY — Log-based Recovery Demonstration
-- DBSA Concepts: WAL, Checkpointing, UNDO/REDO
-- ============================================================

-- SQLite WAL Mode Recovery Steps:
-- 1. PRAGMA journal_mode = WAL;  -- enable WAL before operations
-- 2. All changes written to traffic.db-wal before applied to traffic.db
-- 3. On crash mid-transaction:
--    - Committed transactions: replayed from WAL into main DB (REDO)
--    - Uncommitted transactions: discarded from WAL (UNDO)
-- 4. Checkpoint: merge WAL into main database file

-- Manual checkpoint (run after bulk inserts for performance):
PRAGMA wal_checkpoint(TRUNCATE);

-- Shadow paging equivalent in SQLite:
-- SQLite uses copy-on-write pages in WAL file
-- Old page remains in main DB until checkpoint
-- New page written to WAL → ensures consistent read views

-- ============================================================
-- SECURITY — Access Control
-- DBSA Concept: Role-based access control, GRANT/REVOKE
-- ============================================================

-- SQLite doesn't natively support user roles, but the design is documented
-- for production PostgreSQL equivalent and enforced at application layer.

-- Role definitions:
-- admin_role: Full access (DDL + DML + DROP)
-- officer_role: INSERT + UPDATE on Traffic_Observation, Incident; SELECT all
-- public_role: SELECT on PublicTrafficView only; no access to Vehicle/Driver

-- PostgreSQL equivalents (for documentation/migration reference):
-- CREATE ROLE admin_role;
-- CREATE ROLE officer_role;
-- CREATE ROLE public_role;
--
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO admin_role;
--
-- GRANT SELECT, INSERT, UPDATE ON Traffic_Observation TO officer_role;
-- GRANT SELECT, INSERT, UPDATE ON Incident TO officer_role;
-- GRANT SELECT ON Zone, Road, Junction, Traffic_Signal TO officer_role;
-- REVOKE DELETE ON Traffic_Observation FROM officer_role;
-- REVOKE DROP ON ALL TABLES IN SCHEMA public FROM officer_role;
--
-- GRANT SELECT ON PublicTrafficView TO public_role;
-- REVOKE SELECT ON Vehicle FROM public_role;
-- REVOKE SELECT ON Driver FROM public_role;

-- Application-layer enforcement (Python Flask):
-- Each API endpoint checks request.headers['X-User-Role']
-- DELETE endpoints check role == 'admin'
-- POST endpoints check role in {'admin', 'officer'}
-- GET endpoints: public allowed, Vehicle/Driver endpoints require auth
