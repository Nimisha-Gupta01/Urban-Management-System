-- ============================================================
-- Urban Road & Real-Time Traffic Management System
-- BITS Pilani WILP | SESAP ZC337
-- seed_data.sql — Realistic Bengaluru data for all 10 tables
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- ZONES (5 zones in Bengaluru)
-- ============================================================
INSERT INTO Zone(zone_name, city, area_sqkm, zone_type) VALUES
('Whitefield',    'Bengaluru', 28.5, 'IT Corridor'),
('Indiranagar',   'Bengaluru', 12.3, 'Commercial'),
('Koramangala',   'Bengaluru', 14.7, 'Mixed'),
('Jayanagar',     'Bengaluru', 18.2, 'Residential'),
('Hebbal',        'Bengaluru', 22.1, 'Mixed');

-- ============================================================
-- ROADS (20 roads across Bengaluru)
-- ============================================================
INSERT INTO Road(road_name, road_type, length_km, num_lanes, speed_limit, surface_type, direction_type, zone_id) VALUES
('Outer Ring Road - Whitefield Segment', 'Ring Road',       12.4, 6, 80, 'Asphalt',   'Divided',   1),
('ITPL Main Road',                        'City Road',        3.2, 4, 40, 'Asphalt',   'Two-way',   1),
('Hoodi Junction Road',                   'City Road',        2.1, 4, 40, 'Asphalt',   'Two-way',   1),
('100 Feet Road Indiranagar',             'City Road',        4.5, 4, 50, 'Asphalt',   'Two-way',   2),
('CMH Road',                              'City Road',        3.8, 4, 40, 'Asphalt',   'Two-way',   2),
('Airport Road Indiranagar',              'State Highway',    8.2, 6, 60, 'Asphalt',   'Divided',   2),
('Sarjapur Road',                         'City Road',        9.6, 4, 50, 'Asphalt',   'Two-way',   3),
('Inner Ring Road Koramangala',           'Ring Road',        6.3, 4, 60, 'Asphalt',   'Divided',   3),
('80 Feet Road Koramangala',              'City Road',        2.8, 4, 40, 'Asphalt',   'Two-way',   3),
('Jayanagar 11th Main Road',              'City Road',        3.5, 2, 40, 'Asphalt',   'Two-way',   4),
('Bannerghatta Road',                     'State Highway',   14.2, 6, 60, 'Asphalt',   'Divided',   4),
('JP Nagar 1st Phase Road',               'City Road',        4.1, 2, 40, 'Asphalt',   'Two-way',   4),
('Hebbal Flyover Approach Road',          'Flyover',          1.8, 6, 80, 'Concrete',  'Divided',   5),
('Bellary Road NH-44',                    'National Highway', 18.5, 8, 100, 'Asphalt',  'Divided',   5),
('Thanisandra Main Road',                 'City Road',        5.7, 4, 50, 'Asphalt',   'Two-way',   5),
('HAL Old Airport Road',                  'City Road',        7.1, 4, 50, 'Asphalt',   'Two-way',   2),
('MG Road',                               'City Road',        4.9, 4, 40, 'Asphalt',   'Divided',   2),
('Silk Board Junction Road',              'City Road',        2.3, 4, 40, 'Asphalt',   'Two-way',   3),
('Electronic City Phase 1 Road',          'City Road',        6.8, 4, 60, 'Asphalt',   'Two-way',   1),
('KR Puram Bridge Road',                  'City Road',        3.2, 4, 50, 'Asphalt',   'Two-way',   1);

-- ============================================================
-- JUNCTIONS (15 junctions)
-- ============================================================
INSERT INTO Junction(junction_name, junction_type, latitude, longitude, signal_controlled, zone_id) VALUES
('ITPL Main Junction',          'Signalised',   12.9857, 77.7280, 1, 1),
('Hoodi Junction',              'Signalised',   12.9971, 77.6978, 1, 1),
('Kundalahalli Gate',           'Signalised',   12.9769, 77.7102, 1, 1),
('Indiranagar 100 Feet Signal', 'Signalised',   12.9784, 77.6408, 1, 2),
('Domlur Flyover Junction',     'Flyover',      12.9613, 77.6384, 0, 2),
('Silk Board Junction',         'Signalised',   12.9165, 77.6227, 1, 3),
('Iblur Junction',              'Signalised',   12.9274, 77.6612, 1, 3),
('Koramangala 5th Block',       'Signalised',   12.9363, 77.6236, 1, 3),
('Jayanagar 4th Block',         'Signalised',   12.9328, 77.5825, 1, 4),
('JP Nagar Roundabout',         'Roundabout',   12.9079, 77.5839, 0, 4),
('Bannerghatta Road Junction',  'Signalised',   12.9102, 77.5961, 1, 4),
('Hebbal Flyover Signal',       'Signalised',   13.0454, 77.5971, 1, 5),
('Nagawara Junction',           'Signalised',   13.0429, 77.6194, 1, 5),
('Thanisandra Junction',        'Signalised',   13.0612, 77.6312, 1, 5),
('KR Puram Bridge Junction',    'Signalised',   12.9941, 77.6958, 1, 1);

-- ============================================================
-- ROAD_JUNCTION (bridge table — M:N relationships)
-- ============================================================
INSERT INTO Road_Junction(road_id, junction_id, position_type) VALUES
(1,  1, 'Intermediate'), (1,  2, 'Intermediate'), (1, 15, 'End'),
(2,  1, 'Start'),        (2,  3, 'End'),
(3,  2, 'Start'),        (3, 15, 'End'),
(4,  4, 'Start'),        (4,  5, 'End'),
(6,  4, 'Intermediate'), (6, 12, 'Start'),
(7,  6, 'Start'),        (7,  7, 'End'),
(8,  6, 'Intermediate'), (8,  8, 'End'),
(11, 9, 'Start'),        (11, 11, 'End'),
(13, 12, 'Start'),       (14, 12, 'Intermediate'), (14, 13, 'End'),
(15, 13, 'Start'),       (15, 14, 'End');

-- ============================================================
-- TRAFFIC SIGNALS
-- ============================================================
INSERT INTO Traffic_Signal(junction_id, signal_type, installed_date, operational_status, green_duration_sec) VALUES
(1, 'Adaptive',   '2022-03-15', 'Active',             45),
(2, 'Standard',   '2020-06-10', 'Active',             60),
(3, 'Standard',   '2021-01-20', 'Active',             45),
(4, 'Adaptive',   '2023-07-01', 'Active',             30),
(6, 'Standard',   '2019-08-14', 'Faulty',             60),
(7, 'Standard',   '2021-11-05', 'Active',             45),
(8, 'Pedestrian', '2022-09-20', 'Active',             30),
(9, 'Standard',   '2020-03-12', 'Active',             60),
(11,'Standard',   '2021-05-18', 'Under Maintenance',  45),
(12,'Adaptive',   '2023-02-28', 'Active',             40);

-- ============================================================
-- DRIVERS (20 drivers with Karnataka license numbers)
-- ============================================================
INSERT INTO Driver(name, license_no, dob, contact, address) VALUES
('Rajesh Kumar',      'KA01 20180042312', '1985-04-12', '9845012345', 'Whitefield, Bengaluru'),
('Priya Sharma',      'KA02 20190065431', '1990-07-22', '9845067890', 'Indiranagar, Bengaluru'),
('Mohammed Aziz',     'KA01 20170034521', '1982-11-08', '9741234567', 'Koramangala, Bengaluru'),
('Sunita Reddy',      'KA03 20200078912', '1995-02-14', '8765432109', 'Jayanagar, Bengaluru'),
('Vikram Singh',      'KA04 20160023451', '1978-09-30', '9900112233', 'Hebbal, Bengaluru'),
('Anitha Nair',       'KA05 20210090123', '1992-06-18', '8901234567', 'Whitefield, Bengaluru'),
('Suresh Babu',       'KA01 20150011234', '1975-12-05', '9876543210', 'Indiranagar, Bengaluru'),
('Kavitha Murthy',    'KA02 20180055678', '1988-03-27', '9123456789', 'Koramangala, Bengaluru'),
('Deepak Joshi',      'KA03 20190044321', '1993-08-15', '9234567891', 'Jayanagar, Bengaluru'),
('Meena Krishnan',    'KA04 20200033210', '1991-01-20', '9345678912', 'Hebbal, Bengaluru'),
('Arun Venkatesh',    'KA05 20170022109', '1983-05-10', '9456789123', 'Whitefield, Bengaluru'),
('Rekha Pillai',      'KA01 20210011098', '1996-10-25', '9567891234', 'Indiranagar, Bengaluru'),
('Girish Patil',      'KA02 20160044567', '1980-07-14', '9678912345', 'Koramangala, Bengaluru'),
('Bhavana Rao',       'KA03 20220033456', '1997-04-02', '9789123456', 'Jayanagar, Bengaluru'),
('Kiran Desai',       'KA04 20150022345', '1977-11-19', '9890234567', '  Hebbal, Bengaluru'),
('Satish Gowda',      'KA05 20180011234', '1986-02-28', '9901345678', 'Whitefield, Bengaluru'),
('Lakshmi Iyer',      'KA01 20190077654', '1994-09-07', '8012456789', 'Indiranagar, Bengaluru'),
('Ravi Shankar',      'KA02 20170066543', '1981-06-16', '8123567890', 'Koramangala, Bengaluru'),
('Usha Shetty',       'KA03 20210055432', '1989-03-23', '8234678901', 'Jayanagar, Bengaluru'),
('Nagaraj Kulkarni',  'KA04 20160044321', '1976-12-11', '8345789012', 'Hebbal, Bengaluru');

-- ============================================================
-- VEHICLES (25 vehicles with Karnataka registration plates)
-- ============================================================
INSERT INTO Vehicle(license_plate, vehicle_type, make, model, year, registered_state, owner_id) VALUES
('KA-01-AB-1234', 'Car',        'Maruti',  'Swift',       2020, 'Karnataka', 1),
('KA-02-CD-5678', 'Car',        'Hyundai', 'i20',         2021, 'Karnataka', 2),
('KA-01-EF-9012', 'Truck',      'Tata',    'LPT 1615',    2019, 'Karnataka', 3),
('KA-03-GH-3456', 'Car',        'Honda',   'City',        2022, 'Karnataka', 4),
('KA-04-IJ-7890', 'Bus',        'Volvo',   'B7R',         2018, 'Karnataka', 5),
('KA-05-KL-2345', 'Motorcycle', 'Bajaj',   'Pulsar 150',  2021, 'Karnataka', 6),
('KA-01-MN-6789', 'Car',        'Toyota',  'Innova',      2020, 'Karnataka', 7),
('KA-02-OP-0123', 'Car',        'Mahindra','XUV500',      2019, 'Karnataka', 8),
('KA-03-QR-4567', 'Motorcycle', 'Hero',    'Splendor',    2022, 'Karnataka', 9),
('KA-04-ST-8901', 'Car',        'Kia',     'Seltos',      2023, 'Karnataka', 10),
('KA-05-UV-2345', 'Truck',      'Ashok',   'Viking 4923', 2017, 'Karnataka', 11),
('KA-01-WX-6789', 'Car',        'Renault', 'Kwid',        2021, 'Karnataka', 12),
('KA-02-YZ-0123', 'Auto',       'Bajaj',   'RE 4S',       2020, 'Karnataka', 13),
('KA-03-AA-4567', 'Car',        'Maruti',  'Dzire',       2022, 'Karnataka', 14),
('KA-04-BB-8901', 'Bus',        'TATA',    'Starbus',     2019, 'Karnataka', 15),
('KA-05-CC-2345', 'Car',        'Hyundai', 'Creta',       2023, 'Karnataka', 16),
('KA-01-DD-6789', 'Motorcycle', 'Royal',   'Meteor 350',  2022, 'Karnataka', 17),
('KA-02-EE-0123', 'Car',        'VW',      'Polo',        2020, 'Karnataka', 18),
('KA-03-FF-4567', 'Truck',      'Eicher',  '20.14',       2018, 'Karnataka', 19),
('KA-04-GG-8901', 'Car',        'Tata',    'Nexon EV',    2023, 'Karnataka', 20),
('KA-05-HH-2345', 'Car',        'Maruti',  'Baleno',      2021, 'Karnataka', 1),
('KA-01-II-6789', 'Car',        'Ford',    'EcoSport',    2019, 'Karnataka', 2),
('KA-02-JJ-0123', 'Auto',       'TVS',     'King',        2021, 'Karnataka', 3),
('KA-03-KK-4567', 'Motorcycle', 'TVS',     'Apache RTR',  2022, 'Karnataka', 4),
('KA-04-LL-8901', 'Car',        'Nissan',  'Magnite',     2022, 'Karnataka', 5);

-- ============================================================
-- SENSORS (10 sensors)
-- ============================================================
INSERT INTO Sensor(sensor_type, junction_id, installation_date, status, last_reading_time) VALUES
('Inductive Loop', 1, '2022-03-15', 'Active',   datetime('now', '-5 minutes')),
('Camera',         1, '2022-03-15', 'Active',   datetime('now', '-5 minutes')),
('Radar',          2, '2020-06-10', 'Active',   datetime('now', '-3 minutes')),
('Inductive Loop', 4, '2023-07-01', 'Active',   datetime('now', '-7 minutes')),
('Camera',         6, '2019-08-14', 'Faulty',   datetime('now', '-2 hours')),
('Radar',          7, '2021-11-05', 'Active',   datetime('now', '-4 minutes')),
('CCTV',           8, '2022-09-20', 'Active',   datetime('now', '-6 minutes')),
('Inductive Loop', 9, '2020-03-12', 'Active',   datetime('now', '-8 minutes')),
('Camera',        12, '2023-02-28', 'Active',   datetime('now', '-2 minutes')),
('Microwave',     15, '2021-04-10', 'Inactive', datetime('now', '-3 days'));

-- ============================================================
-- TRAFFIC OBSERVATIONS (100 observations — realistic Bengaluru traffic)
-- ============================================================
-- Peak morning rush (7-10 AM), off-peak (11AM-5PM), evening rush (5-9PM)
INSERT INTO Traffic_Observation(junction_id, road_id, observation_time, vehicle_count, avg_speed_kmph, congestion_level, weather_condition, data_source) VALUES
-- Silk Board Junction (junction 6) — notorious for congestion
(6,  7,  datetime('now', '-23 hours'), 312, 8.2,  'SEVERE',   'Rainy',  'Sensor'),
(6,  7,  datetime('now', '-22 hours'), 289, 12.5, 'SEVERE',   'Rainy',  'Sensor'),
(6,  8,  datetime('now', '-21 hours'), 245, 18.3, 'HIGH',     'Rainy',  'Camera'),
(6,  7,  datetime('now', '-20 hours'), 198, 22.1, 'HIGH',     'Clear',  'Sensor'),
(6,  7,  datetime('now', '-19 hours'), 156, 28.4, 'MODERATE', 'Clear',  'Sensor'),
(6,  8,  datetime('now', '-18 hours'), 134, 31.2, 'MODERATE', 'Clear',  'Camera'),
(6,  7,  datetime('now', '-17 hours'), 112, 38.5, 'LOW',      'Clear',  'Sensor'),
(6,  7,  datetime('now', '-16 hours'), 89,  45.0, 'LOW',      'Clear',  'Sensor'),
-- Evening rush at Silk Board
(6,  7,  datetime('now', '-5 hours'),  278, 10.1, 'SEVERE',   'Clear',  'Sensor'),
(6,  7,  datetime('now', '-4 hours'),  256, 14.3, 'SEVERE',   'Cloudy', 'Sensor'),
(6,  8,  datetime('now', '-3 hours'),  221, 19.8, 'HIGH',     'Cloudy', 'Camera'),
(6,  7,  datetime('now', '-2 hours'),  187, 25.6, 'HIGH',     'Clear',  'Sensor'),
(6,  7,  datetime('now', '-1 hour'),   142, 33.4, 'MODERATE', 'Clear',  'Sensor'),
-- ITPL Junction (junction 1) — IT corridor morning rush
(1,  2,  datetime('now', '-22 hours'), 267, 15.2, 'SEVERE',   'Clear',  'Sensor'),
(1,  2,  datetime('now', '-21 hours'), 243, 19.8, 'HIGH',     'Clear',  'Camera'),
(1,  2,  datetime('now', '-20 hours'), 198, 24.5, 'HIGH',     'Clear',  'Sensor'),
(1,  1,  datetime('now', '-19 hours'), 165, 31.2, 'MODERATE', 'Clear',  'Sensor'),
(1,  2,  datetime('now', '-5 hours'),  234, 17.3, 'HIGH',     'Clear',  'Sensor'),
(1,  2,  datetime('now', '-4 hours'),  212, 21.1, 'HIGH',     'Clear',  'Camera'),
(1,  2,  datetime('now', '-3 hours'),  187, 27.4, 'MODERATE', 'Clear',  'Sensor'),
(1,  2,  datetime('now', '-1 hour'),   98,  42.3, 'LOW',      'Clear',  'Sensor'),
-- Indiranagar junction (junction 4)
(4,  4,  datetime('now', '-22 hours'), 198, 22.3, 'HIGH',     'Clear',  'Sensor'),
(4,  4,  datetime('now', '-21 hours'), 176, 27.8, 'MODERATE', 'Clear',  'Camera'),
(4,  6,  datetime('now', '-20 hours'), 154, 32.1, 'MODERATE', 'Clear',  'Sensor'),
(4,  4,  datetime('now', '-5 hours'),  213, 19.4, 'HIGH',     'Rainy',  'Sensor'),
(4,  4,  datetime('now', '-4 hours'),  234, 15.6, 'HIGH',     'Rainy',  'Sensor'),
(4,  6,  datetime('now', '-3 hours'),  189, 23.2, 'HIGH',     'Rainy',  'Camera'),
(4,  4,  datetime('now', '-2 hours'),  145, 31.8, 'MODERATE', 'Clear',  'Sensor'),
-- Hebbal Flyover (junction 12) — airport traffic
(12, 13, datetime('now', '-20 hours'), 287, 45.2, 'HIGH',     'Clear',  'Camera'),
(12, 14, datetime('now', '-19 hours'), 312, 38.1, 'SEVERE',   'Clear',  'Camera'),
(12, 13, datetime('now', '-18 hours'), 245, 51.3, 'HIGH',     'Clear',  'Sensor'),
(12, 14, datetime('now', '-17 hours'), 198, 62.4, 'MODERATE', 'Clear',  'Sensor'),
(12, 13, datetime('now', '-5 hours'),  267, 43.2, 'HIGH',     'Clear',  'Camera'),
(12, 14, datetime('now', '-4 hours'),  289, 41.1, 'HIGH',     'Clear',  'Camera'),
-- Koramangala (junction 8)
(8,  8,  datetime('now', '-22 hours'), 156, 28.5, 'MODERATE', 'Clear',  'Sensor'),
(8,  9,  datetime('now', '-21 hours'), 134, 33.2, 'MODERATE', 'Clear',  'Camera'),
(8,  8,  datetime('now', '-20 hours'), 112, 38.7, 'LOW',      'Clear',  'Sensor'),
(8,  9,  datetime('now', '-5 hours'),  178, 24.3, 'MODERATE', 'Clear',  'Sensor'),
(8,  8,  datetime('now', '-4 hours'),  201, 19.8, 'HIGH',     'Cloudy', 'Camera'),
-- Hoodi Junction (junction 2)
(2,  3,  datetime('now', '-22 hours'), 189, 26.4, 'HIGH',     'Clear',  'Sensor'),
(2,  1,  datetime('now', '-21 hours'), 167, 31.2, 'MODERATE', 'Clear',  'Sensor'),
(2,  3,  datetime('now', '-5 hours'),  212, 22.1, 'HIGH',     'Clear',  'Sensor'),
(2,  1,  datetime('now', '-4 hours'),  234, 17.5, 'HIGH',     'Clear',  'Camera'),
-- Jayanagar (junction 9)
(9,  10, datetime('now', '-22 hours'), 143, 32.1, 'MODERATE', 'Clear',  'Manual'),
(9,  11, datetime('now', '-21 hours'), 121, 37.8, 'LOW',      'Clear',  'Manual'),
(9,  10, datetime('now', '-5 hours'),  165, 28.4, 'MODERATE', 'Clear',  'Manual'),
-- Current observations (last 30 mins)
(6,  7,  datetime('now', '-30 minutes'), 234, 16.8, 'HIGH',     'Clear',  'Sensor'),
(1,  2,  datetime('now', '-28 minutes'), 189, 22.3, 'HIGH',     'Clear',  'Camera'),
(4,  4,  datetime('now', '-25 minutes'), 156, 29.1, 'MODERATE', 'Rainy',  'Sensor'),
(12, 14, datetime('now', '-20 minutes'), 267, 48.2, 'HIGH',     'Clear',  'Camera'),
(8,  8,  datetime('now', '-18 minutes'), 143, 34.5, 'MODERATE', 'Clear',  'Sensor'),
(2,  3,  datetime('now', '-15 minutes'), 178, 27.8, 'MODERATE', 'Clear',  'Sensor'),
(7,  7,  datetime('now', '-12 minutes'), 112, 38.4, 'LOW',      'Clear',  'Sensor'),
(3,  2,  datetime('now', '-10 minutes'), 134, 33.2, 'MODERATE', 'Clear',  'Camera'),
(9,  10, datetime('now', '-8 minutes'),  98,  41.2, 'LOW',      'Clear',  'Manual'),
(11, 11, datetime('now', '-5 minutes'),  167, 31.5, 'MODERATE', 'Clear',  'Manual'),
-- Additional observations to reach ~100
(6,  7,  datetime('now', '-15 hours'), 78,  52.3, 'LOW',      'Clear',  'Sensor'),
(6,  7,  datetime('now', '-14 hours'), 65,  58.1, 'LOW',      'Clear',  'Sensor'),
(6,  7,  datetime('now', '-13 hours'), 92,  47.2, 'LOW',      'Clear',  'Sensor'),
(1,  2,  datetime('now', '-15 hours'), 54,  61.4, 'LOW',      'Clear',  'Sensor'),
(1,  2,  datetime('now', '-14 hours'), 67,  56.8, 'LOW',      'Clear',  'Sensor'),
(1,  2,  datetime('now', '-13 hours'), 89,  49.3, 'LOW',      'Cloudy', 'Sensor'),
(4,  4,  datetime('now', '-15 hours'), 76,  53.7, 'LOW',      'Clear',  'Sensor'),
(4,  4,  datetime('now', '-14 hours'), 83,  50.2, 'LOW',      'Clear',  'Camera'),
(12, 13, datetime('now', '-15 hours'), 145, 67.8, 'MODERATE', 'Clear',  'Camera'),
(12, 14, datetime('now', '-14 hours'), 167, 61.2, 'MODERATE', 'Clear',  'Camera'),
(8,  9,  datetime('now', '-15 hours'), 87,  48.6, 'LOW',      'Clear',  'Sensor'),
(8,  8,  datetime('now', '-14 hours'), 95,  44.3, 'LOW',      'Clear',  'Sensor'),
(2,  3,  datetime('now', '-15 hours'), 112, 41.2, 'LOW',      'Clear',  'Sensor'),
(9,  11, datetime('now', '-15 hours'), 78,  52.1, 'LOW',      'Clear',  'Manual'),
(13, 15, datetime('now', '-20 hours'), 134, 38.7, 'MODERATE', 'Clear',  'Camera'),
(13, 15, datetime('now', '-5 hours'),  189, 28.4, 'MODERATE', 'Clear',  'Camera'),
(14, 15, datetime('now', '-20 hours'), 145, 35.6, 'MODERATE', 'Clear',  'Sensor'),
(15, 15, datetime('now', '-20 hours'), 98,  44.2, 'LOW',      'Clear',  'Manual'),
(10, 11, datetime('now', '-20 hours'), 87,  47.8, 'LOW',      'Clear',  'Manual'),
(11, 11, datetime('now', '-20 hours'), 145, 35.2, 'MODERATE', 'Clear',  'Manual'),
(5,  5,  datetime('now', '-20 hours'), 112, 41.3, 'LOW',      'Clear',  'Manual'),
(5,  4,  datetime('now', '-5 hours'),  178, 27.6, 'MODERATE', 'Foggy',  'Camera'),
(3,  3,  datetime('now', '-22 hours'), 167, 29.8, 'MODERATE', 'Clear',  'Sensor'),
(3,  3,  datetime('now', '-5 hours'),  198, 24.5, 'HIGH',     'Clear',  'Sensor'),
(7,  8,  datetime('now', '-22 hours'), 134, 35.4, 'MODERATE', 'Clear',  'Sensor'),
(7,  8,  datetime('now', '-5 hours'),  156, 31.2, 'MODERATE', 'Clear',  'Sensor'),
-- Rainy day observations (week ago)
(6,  7,  datetime('now', '-7 days', '+7 hours'), 334, 7.2,  'SEVERE',   'Rainy', 'Sensor'),
(6,  7,  datetime('now', '-7 days', '+8 hours'), 356, 5.8,  'SEVERE',   'Rainy', 'Camera'),
(1,  2,  datetime('now', '-7 days', '+7 hours'), 289, 11.3, 'SEVERE',   'Rainy', 'Sensor'),
(12, 14, datetime('now', '-7 days', '+7 hours'), 312, 35.2, 'HIGH',     'Rainy', 'Camera'),
(4,  4,  datetime('now', '-7 days', '+8 hours'), 267, 14.8, 'SEVERE',   'Rainy', 'Sensor');

-- ============================================================
-- INCIDENTS (30 incidents)
-- ============================================================
INSERT INTO Incident(incident_type, severity, description, reported_datetime, resolved_datetime, road_id, junction_id, vehicle_id, reported_by) VALUES
-- Open incidents
('Accident',   'HIGH',     'Two-vehicle collision at Silk Board, partial road block',   datetime('now', '-2 hours'),   NULL,                          7,  6, 1,  'Traffic Control Room'),
('Breakdown',  'MEDIUM',   'Heavy truck engine failure blocking left lane on ORR',      datetime('now', '-3 hours'),   NULL,                          1,  2, 3,  'BBMP Helpline 1533'),
('Flooding',   'HIGH',     'Waterlogging after heavy rain, 3 lanes submerged',          datetime('now', '-4 hours'),   NULL,                          4,  4, NULL, 'Citizen Report'),
('Roadblock',  'MEDIUM',   'VIP convoy scheduled at Hebbal Flyover',                   datetime('now', '-1 hour'),    NULL,                          13,12, NULL, 'Police Control Room'),
('Accident',   'CRITICAL', 'Multi-vehicle pileup on Bellary Road NH-44, 3 vehicles',   datetime('now', '-5 hours'),   NULL,                          14,12, 5,  'Traffic Control Room'),
('Breakdown',  'LOW',      'Two-wheeler breakdown at Koramangala 5th Block signal',     datetime('now', '-90 minutes'),NULL,                          8,  8, 6,  'Self-reported'),
('Accident',   'MEDIUM',   'Minor rear-end collision at Indiranagar signal',            datetime('now', '-6 hours'),   NULL,                          4,  4, 7,  'Traffic Control Room'),
('Flooding',   'MEDIUM',   'Minor waterlogging on CMH Road underpass',                 datetime('now', '-8 hours'),   NULL,                          5,  NULL, NULL,'BBMP'),
-- Resolved incidents (last 24 hours)
('Accident',   'HIGH',     'Bus vs car collision on ITPL Main Road, both drivable',    datetime('now', '-20 hours'),  datetime('now', '-17 hours'),  2,  1, 8,  'Traffic Control Room'),
('Breakdown',  'LOW',      'Auto breakdown cleared on Jayanagar 11th Main',            datetime('now', '-18 hours'),  datetime('now', '-17 hours'),  10, 9, 13, 'Towing Service'),
('Roadblock',  'LOW',      'Tree fallen on Thanisandra Main Road, cleared by BBMP',    datetime('now', '-16 hours'),  datetime('now', '-14 hours'),  15,14, NULL,'BBMP Helpline'),
('Accident',   'MEDIUM',   'Two-wheeler skid on Sarjapur Road, single vehicle',        datetime('now', '-15 hours'),  datetime('now', '-13 hours'),  7,  7, 9,  'Ambulance'),
('Flooding',   'HIGH',     'Severe waterlogging on Bannerghatta Road underpass',       datetime('now', '-14 hours'),  datetime('now', '-10 hours'),  11,11, NULL,'Traffic Control Room'),
('Breakdown',  'MEDIUM',   'Bus breakdown at Silk Board Junction, 30 min delay',       datetime('now', '-12 hours'),  datetime('now', '-10 hours'),  7,  6, 15, 'BMTC Control Room'),
('Accident',   'LOW',      'Minor parking collision at MG Road, no injury',            datetime('now', '-10 hours'),  datetime('now', '-9 hours'),   17, NULL, 18, 'Self-reported'),
-- Older incidents (last week)
('Accident',   'HIGH',     'Head-on collision at KR Puram Bridge, 2 injured',          datetime('now', '-3 days'),    datetime('now', '-3 days', '+2 hours'), 20,15, 20, 'Traffic Control Room'),
('Flooding',   'CRITICAL', 'Complete road closure due to flooding at Silk Board',      datetime('now', '-7 days', '+8 hours'), datetime('now', '-7 days', '+14 hours'), 7, 6, NULL, 'Traffic Control Room'),
('Accident',   'CRITICAL', 'Truck overturned on Bellary Road, road blocked 4 hours',  datetime('now', '-5 days'),    datetime('now', '-5 days', '+4 hours'), 14,12, 11, 'Traffic Control Room'),
('Roadblock',  'HIGH',     'Road repair work on Outer Ring Road, 2 lanes closed',     datetime('now', '-4 days'),    datetime('now', '-2 days'),    1,  1, NULL,'BBMP'),
('Breakdown',  'MEDIUM',   'Container truck breakdown on Electronic City road',        datetime('now', '-4 days'),    datetime('now', '-4 days', '+3 hours'), 19, NULL, NULL, 'Highway Patrol'),
('Accident',   'MEDIUM',   'Bus vs auto collision near Hebbal Signal',                datetime('now', '-6 days'),    datetime('now', '-6 days', '+1 hour'),  13,12, 5,  'Traffic Control Room'),
('Flooding',   'HIGH',     'Airport Road flooded after thunderstorm',                 datetime('now', '-7 days'),    datetime('now', '-7 days', '+6 hours'), 6,  NULL, NULL,'BBMP'),
('Accident',   'LOW',      'Motorcycle skid at Hoodi Junction, rider minor injury',   datetime('now', '-2 days'),    datetime('now', '-2 days', '+30 minutes'), 3, 2, 6, 'Ambulance'),
('Roadblock',  'LOW',      'Political rally procession on 100 Feet Road',             datetime('now', '-6 days'),    datetime('now', '-6 days', '+3 hours'), 4, 4, NULL,'Police'),
('Breakdown',  'LOW',      'BESCOM work truck stalled on Sarjapur Road',              datetime('now', '-3 days'),    datetime('now', '-3 days', '+1 hour'),  7, NULL, NULL, 'BESCOM'),
('Accident',   'MEDIUM',   'Car hit barrier on Outer Ring Road flyover approach',     datetime('now', '-8 days'),    datetime('now', '-8 days', '+2 hours'), 1, 1, 1, 'Traffic Control Room'),
('Flooding',   'MEDIUM',   'Waterlogging at Koramangala 80 Feet Road underpass',      datetime('now', '-9 days'),    datetime('now', '-9 days', '+4 hours'), 9, NULL, NULL, 'Citizen Report'),
('Breakdown',  'MEDIUM',   'Ambulance tyre burst near Hebbal, caused traffic',        datetime('now', '-10 days'),   datetime('now', '-10 days', '+45 minutes'), 14,12, NULL, 'Police Control Room'),
('Accident',   'HIGH',     'Tourist bus collision near MG Road junction',             datetime('now', '-12 days'),   datetime('now', '-12 days', '+3 hours'), 17, NULL, 15, 'Traffic Control Room'),
('Roadblock',  'HIGH',     'Infrastructure collapse — water main burst on ORR',      datetime('now', '-14 days'),   datetime('now', '-12 days'),    1, NULL, NULL, 'BBMP Emergency');

-- ============================================================
-- EER SPECIALISATION DATA
-- ============================================================
INSERT INTO Incident_Accident(incident_id, injuries_count, fatalities) VALUES
(1, 2, 0), (5, 4, 1), (9, 1, 0), (12, 1, 0), (16, 2, 0),
(18, 0, 0), (21, 2, 0), (23, 1, 0), (26, 0, 0), (29, 3, 0);

INSERT INTO Incident_Flooding(incident_id, water_level_cm) VALUES
(3, 45.0), (8, 15.0), (13, 62.0), (17, 78.0), (22, 55.0),
(27, 25.0), (28, 18.0);

INSERT INTO Incident_Roadblock(incident_id, authority_name) VALUES
(4, 'Bengaluru City Police'), (11, 'BBMP Road Division'),
(19, 'BBMP Maintenance'), (24, 'City Police');

INSERT INTO Incident_Breakdown(incident_id, breakdown_cause) VALUES
(2, 'Engine failure'), (6, 'Tyre puncture'), (10, 'Battery dead'),
(14, 'Fuel exhaustion'), (20, 'Axle failure'), (25, 'Mechanical fault');

INSERT INTO Vehicle_Car(vehicle_id, num_doors, fuel_type) VALUES
(1, 4, 'Petrol'), (2, 4, 'Petrol'), (4, 4, 'Petrol'),
(7, 4, 'Petrol'), (8, 4, 'Diesel'), (10, 4, 'Petrol'),
(12, 4, 'Petrol'), (14, 4, 'Petrol'), (16, 4, 'Petrol'),
(18, 4, 'Petrol'), (20, 4, 'Electric'), (21, 4, 'Petrol'),
(22, 4, 'Petrol'), (25, 4, 'Petrol');

INSERT INTO Vehicle_Truck(vehicle_id, max_load_tonnes) VALUES
(3, 15.0), (11, 20.0), (19, 12.0);

INSERT INTO Vehicle_Motorcycle(vehicle_id, engine_cc) VALUES
(6, 150), (9, 100), (17, 350), (24, 160);

INSERT INTO Vehicle_Bus(vehicle_id, seating_capacity) VALUES
(5, 45), (15, 52);
