-- Urban Road & Real-Time Traffic Management System
-- queries.sql — Sample SQL queries (to be expanded in Phase 4)
-- Status: Placeholder — fill after schema.sql is finalised

-- Simple: All roads in a zone
-- SELECT r.road_name, r.speed_limit, r.num_lanes
-- FROM Road r JOIN Zone z ON r.zone_id = z.zone_id
-- WHERE z.zone_name = 'Whitefield';

-- Medium: Top 5 congested junctions in last 24 hours
-- SELECT j.junction_name, AVG(t.congestion_level) AS avg_congestion
-- FROM Traffic_Observation t JOIN Junction j ON t.junction_id = j.junction_id
-- WHERE t.observation_time >= datetime('now', '-1 day')
-- GROUP BY j.junction_id ORDER BY avg_congestion DESC LIMIT 5;
