-- Urban Road & Real-Time Traffic Management System
-- triggers.sql — Triggers, Views, Stored Procedures
-- Status: Placeholder — fill after SQL queries are done (Phase 4)

-- Example trigger (to implement):
-- Auto-flag junction as HIGH congestion when vehicle_count > 200

-- CREATE TRIGGER congestion_alert
-- AFTER INSERT ON Traffic_Observation
-- WHEN NEW.vehicle_count > 200
-- BEGIN
--     UPDATE Junction
--     SET signal_controlled = 1
--     WHERE junction_id = NEW.junction_id;
-- END;
