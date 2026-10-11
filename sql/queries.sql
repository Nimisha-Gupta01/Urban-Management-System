-- ============================================================
-- Urban Road & Real-Time Traffic Management System
-- BITS Pilani WILP | SESAP ZC337
-- queries.sql — 25 SQL Queries covering all syllabus topics
-- DBSA Concepts: Relational Algebra, SQL joins, aggregates,
--   GROUP BY/HAVING, subqueries, nested queries, EXISTS/IN,
--   Window functions, Views, Query optimization (EXPLAIN)
-- ============================================================

-- ============================================================
-- SECTION 1: SIMPLE SELECT QUERIES (Relational Algebra: σ, π)
-- ============================================================

-- Q1: All roads in Whitefield zone (σ zone_name='Whitefield'(Road ⋈ Zone))
SELECT r.road_id, r.road_name, r.road_type, r.num_lanes, r.speed_limit
FROM Road r
JOIN Zone z ON r.zone_id = z.zone_id
WHERE z.zone_name = 'Whitefield'
ORDER BY r.road_name;

-- Q2: All signalised junctions with their zone
SELECT j.junction_name, j.junction_type, j.latitude, j.longitude, z.zone_name
FROM Junction j
JOIN Zone z ON j.zone_id = z.zone_id
WHERE j.signal_controlled = 1
ORDER BY z.zone_name, j.junction_name;

-- Q3: All active sensors and their junction names
SELECT s.sensor_id, s.sensor_type, j.junction_name, s.last_reading_time
FROM Sensor s
JOIN Junction j ON s.junction_id = j.junction_id
WHERE s.status = 'Active'
ORDER BY s.last_reading_time DESC;

-- ============================================================
-- SECTION 2: AGGREGATE FUNCTIONS
-- ============================================================

-- Q4: Total number of observations per congestion level
SELECT congestion_level, COUNT(*) AS observation_count,
       ROUND(AVG(vehicle_count), 1) AS avg_vehicles,
       ROUND(AVG(avg_speed_kmph), 1) AS avg_speed
FROM Traffic_Observation
GROUP BY congestion_level
ORDER BY observation_count DESC;

-- Q5: Number of incidents by type and severity (cross-tabulation)
SELECT incident_type, severity, COUNT(*) AS count
FROM Incident
GROUP BY incident_type, severity
ORDER BY incident_type, count DESC;

-- Q6: Average speed per road segment (all time)
SELECT r.road_name, r.road_type,
       COUNT(t.obs_id) AS total_observations,
       ROUND(AVG(t.avg_speed_kmph), 2) AS avg_speed_kmph,
       MIN(t.avg_speed_kmph) AS min_speed,
       MAX(t.avg_speed_kmph) AS max_speed
FROM Road r
LEFT JOIN Traffic_Observation t ON r.road_id = t.road_id
GROUP BY r.road_id, r.road_name
HAVING COUNT(t.obs_id) > 0
ORDER BY avg_speed_kmph ASC;

-- ============================================================
-- SECTION 3: JOINS — INNER, LEFT, SELF
-- ============================================================

-- Q7: Top 5 most congested junctions in last 24 hours (INNER JOIN + aggregate)
SELECT j.junction_name, z.zone_name,
       COUNT(t.obs_id) AS obs_count,
       ROUND(AVG(t.vehicle_count), 0) AS avg_vehicles,
       ROUND(AVG(t.avg_speed_kmph), 1) AS avg_speed
FROM Traffic_Observation t
INNER JOIN Junction j ON t.junction_id = j.junction_id
INNER JOIN Zone z ON j.zone_id = z.zone_id
WHERE t.observation_time >= datetime('now', '-1 day')
GROUP BY j.junction_id, j.junction_name, z.zone_name
ORDER BY avg_vehicles DESC
LIMIT 5;

-- Q8: All junctions including those with NO observations today (LEFT JOIN)
SELECT j.junction_name, j.junction_type, z.zone_name,
       COUNT(t.obs_id) AS obs_today,
       MAX(t.vehicle_count) AS peak_vehicles
FROM Junction j
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
    AND DATE(t.observation_time) = DATE('now')
LEFT JOIN Zone z ON j.zone_id = z.zone_id
GROUP BY j.junction_id, j.junction_name, j.junction_type, z.zone_name
ORDER BY obs_today DESC;

-- Q9: Incidents on roads where average speed drops below 30 km/h (complex INNER JOIN)
SELECT i.incident_type, i.severity, r.road_name,
       ROUND(AVG(t.avg_speed_kmph), 1) AS road_avg_speed,
       COUNT(i.incident_id) AS incident_count
FROM Incident i
INNER JOIN Road r ON i.road_id = r.road_id
INNER JOIN Traffic_Observation t ON t.road_id = r.road_id
GROUP BY i.incident_id, i.incident_type, i.severity, r.road_name
HAVING AVG(t.avg_speed_kmph) < 30
ORDER BY road_avg_speed ASC;

-- Q10: Vehicle details with owner information (INNER JOIN across 2 entities)
SELECT v.license_plate, v.vehicle_type, v.make, v.model, v.year,
       d.name AS owner_name, d.license_no, d.contact
FROM Vehicle v
INNER JOIN Driver d ON v.owner_id = d.driver_id
ORDER BY d.name;

-- Q11: Roads and their junctions (M:N join via bridge table)
SELECT r.road_name, r.road_type, j.junction_name, j.junction_type, rj.position_type
FROM Road r
INNER JOIN Road_Junction rj ON r.road_id = rj.road_id
INNER JOIN Junction j ON rj.junction_id = j.junction_id
ORDER BY r.road_name, rj.position_type;

-- ============================================================
-- SECTION 4: GROUP BY / HAVING
-- ============================================================

-- Q12: Zones with more than 3 HIGH or SEVERE congestion incidents today
SELECT z.zone_name,
       COUNT(t.obs_id) AS high_severity_obs,
       ROUND(AVG(t.vehicle_count), 0) AS avg_vehicles
FROM Zone z
INNER JOIN Junction j ON z.zone_id = j.zone_id
INNER JOIN Traffic_Observation t ON j.junction_id = t.junction_id
WHERE t.congestion_level IN ('HIGH','SEVERE')
  AND DATE(t.observation_time) = DATE('now')
GROUP BY z.zone_id, z.zone_name
HAVING COUNT(t.obs_id) > 3
ORDER BY high_severity_obs DESC;

-- Q13: Roads with more than 2 unresolved incidents
SELECT r.road_name, r.road_type, z.zone_name,
       COUNT(i.incident_id) AS open_incidents,
       MAX(i.severity) AS worst_severity
FROM Road r
INNER JOIN Incident i ON r.road_id = i.road_id
INNER JOIN Zone z ON r.zone_id = z.zone_id
WHERE i.resolved_datetime IS NULL
GROUP BY r.road_id, r.road_name, r.road_type, z.zone_name
HAVING COUNT(i.incident_id) > 2
ORDER BY open_incidents DESC;

-- ============================================================
-- SECTION 5: SUBQUERIES AND NESTED QUERIES
-- ============================================================

-- Q14: Junctions with vehicle count above the overall average (correlated subquery)
SELECT j.junction_name, t.observation_time, t.vehicle_count, t.congestion_level
FROM Traffic_Observation t
INNER JOIN Junction j ON t.junction_id = j.junction_id
WHERE t.vehicle_count > (
    SELECT AVG(vehicle_count) FROM Traffic_Observation
)
ORDER BY t.vehicle_count DESC;

-- Q15: Roads that have NEVER had an incident (NOT EXISTS)
SELECT r.road_id, r.road_name, r.road_type, z.zone_name
FROM Road r
INNER JOIN Zone z ON r.zone_id = z.zone_id
WHERE NOT EXISTS (
    SELECT 1 FROM Incident i WHERE i.road_id = r.road_id
)
ORDER BY z.zone_name, r.road_name;

-- Q16: Most recent observation per junction (correlated subquery — dashboard pattern)
SELECT j.junction_name, t.observation_time, t.vehicle_count,
       t.avg_speed_kmph, t.congestion_level, t.weather_condition
FROM Traffic_Observation t
INNER JOIN Junction j ON t.junction_id = j.junction_id
WHERE t.observation_time = (
    SELECT MAX(t2.observation_time)
    FROM Traffic_Observation t2
    WHERE t2.junction_id = t.junction_id
)
ORDER BY j.junction_name;

-- Q17: Vehicles involved in CRITICAL severity incidents (IN subquery)
SELECT v.license_plate, v.vehicle_type, v.make, v.model,
       d.name AS owner_name, d.contact
FROM Vehicle v
INNER JOIN Driver d ON v.owner_id = d.driver_id
WHERE v.vehicle_id IN (
    SELECT vehicle_id FROM Incident
    WHERE severity = 'CRITICAL'
    AND vehicle_id IS NOT NULL
)
ORDER BY v.license_plate;

-- Q18: Zones with average congestion above city average (nested aggregate)
SELECT z.zone_name,
       ROUND(AVG(CASE t.congestion_level
           WHEN 'LOW'      THEN 1
           WHEN 'MODERATE' THEN 2
           WHEN 'HIGH'     THEN 3
           WHEN 'SEVERE'   THEN 4
           ELSE 0 END), 2) AS congestion_score
FROM Zone z
INNER JOIN Junction j ON z.zone_id = j.zone_id
INNER JOIN Traffic_Observation t ON j.junction_id = t.junction_id
GROUP BY z.zone_id, z.zone_name
HAVING AVG(CASE t.congestion_level
    WHEN 'LOW'      THEN 1
    WHEN 'MODERATE' THEN 2
    WHEN 'HIGH'     THEN 3
    WHEN 'SEVERE'   THEN 4
    ELSE 0 END) > (
    SELECT AVG(CASE congestion_level
        WHEN 'LOW'      THEN 1
        WHEN 'MODERATE' THEN 2
        WHEN 'HIGH'     THEN 3
        WHEN 'SEVERE'   THEN 4
        ELSE 0 END)
    FROM Traffic_Observation
)
ORDER BY congestion_score DESC;

-- ============================================================
-- SECTION 6: TIME-SERIES AND WINDOW-STYLE QUERIES
-- ============================================================

-- Q19: Hourly traffic trend for a specific junction (last 12 hours)
SELECT
    strftime('%Y-%m-%d %H:00', observation_time) AS hour_bucket,
    COUNT(*) AS observations,
    ROUND(AVG(vehicle_count), 0) AS avg_vehicles,
    ROUND(AVG(avg_speed_kmph), 1) AS avg_speed,
    MAX(vehicle_count) AS peak_vehicles
FROM Traffic_Observation
WHERE junction_id = 1
  AND observation_time >= datetime('now', '-12 hours')
GROUP BY hour_bucket
ORDER BY hour_bucket;

-- Q20: Rolling 3-observation average for a junction (window-style using subquery)
SELECT
    t1.obs_id,
    t1.observation_time,
    t1.vehicle_count,
    ROUND((
        SELECT AVG(t2.vehicle_count)
        FROM Traffic_Observation t2
        WHERE t2.junction_id = t1.junction_id
          AND t2.obs_id <= t1.obs_id
          AND t2.obs_id >= t1.obs_id - 2
    ), 1) AS rolling_avg_3obs
FROM Traffic_Observation t1
WHERE t1.junction_id = 1
ORDER BY t1.obs_id;

-- Q21: Peak congestion hour across all junctions
SELECT
    strftime('%H', observation_time) AS hour_of_day,
    COUNT(*) AS total_observations,
    ROUND(AVG(vehicle_count), 0) AS avg_vehicles,
    SUM(CASE WHEN congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END) AS high_congestion_obs
FROM Traffic_Observation
GROUP BY hour_of_day
ORDER BY avg_vehicles DESC;

-- ============================================================
-- SECTION 7: MULTI-TABLE ANALYTICAL QUERIES (4-5 table joins)
-- ============================================================

-- Q22: Full incident report (4-table join: Incident-Road-Junction-Zone)
SELECT
    i.incident_id,
    i.incident_type,
    i.severity,
    i.reported_datetime,
    i.resolved_datetime,
    CASE WHEN i.resolved_datetime IS NULL THEN 'OPEN' ELSE 'RESOLVED' END AS status,
    r.road_name,
    j.junction_name,
    z.zone_name,
    i.reported_by
FROM Incident i
LEFT JOIN Road r ON i.road_id = r.road_id
LEFT JOIN Junction j ON i.junction_id = j.junction_id
LEFT JOIN Zone z ON COALESCE(r.zone_id, j.zone_id) = z.zone_id
ORDER BY i.reported_datetime DESC;

-- Q23: Zone performance summary (5-table join: Zone-Junction-Road-Observation-Incident)
SELECT
    z.zone_name,
    COUNT(DISTINCT j.junction_id) AS num_junctions,
    COUNT(DISTINCT r.road_id) AS num_roads,
    COUNT(t.obs_id) AS total_observations,
    ROUND(AVG(t.vehicle_count), 0) AS avg_vehicle_count,
    ROUND(AVG(t.avg_speed_kmph), 1) AS avg_speed,
    COUNT(DISTINCT i.incident_id) AS total_incidents
FROM Zone z
LEFT JOIN Junction j ON z.zone_id = j.zone_id
LEFT JOIN Road r ON z.zone_id = r.zone_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
LEFT JOIN Incident i ON r.road_id = i.road_id
GROUP BY z.zone_id, z.zone_name
ORDER BY total_incidents DESC;

-- Q24: Signal health vs congestion correlation
SELECT
    ts.operational_status AS signal_status,
    COUNT(DISTINCT j.junction_id) AS junctions,
    ROUND(AVG(t.vehicle_count), 0) AS avg_vehicles,
    ROUND(AVG(t.avg_speed_kmph), 1) AS avg_speed,
    SUM(CASE WHEN t.congestion_level IN ('HIGH','SEVERE') THEN 1 ELSE 0 END) AS high_congestion_events
FROM Traffic_Signal ts
INNER JOIN Junction j ON ts.junction_id = j.junction_id
LEFT JOIN Traffic_Observation t ON j.junction_id = t.junction_id
GROUP BY ts.operational_status
ORDER BY avg_vehicles DESC;

-- Q25: EXPLAIN QUERY PLAN — verify index usage on dashboard query
EXPLAIN QUERY PLAN
SELECT j.junction_name, t.observation_time, t.vehicle_count, t.congestion_level
FROM Traffic_Observation t
INNER JOIN Junction j ON t.junction_id = j.junction_id
WHERE t.junction_id = 3
  AND t.observation_time >= datetime('now', '-1 day')
ORDER BY t.observation_time DESC
LIMIT 10;
-- Expected: "SEARCH TABLE Traffic_Observation USING INDEX idx_obs_junction_time (junction_id=? AND observation_time>?)"
-- This confirms B+ tree composite index is used — no full table scan
