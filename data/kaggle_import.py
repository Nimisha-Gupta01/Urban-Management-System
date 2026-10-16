"""
data/kaggle_import.py
Imports Kaggle Bengaluru traffic dataset into Traffic_Observation.

Dataset: asshridattaaigal/bengaluru-traffic (bangalore_routes1.csv)
Columns used: source_location, lat_src, lon_src, hour, day_of_week,
              vehicles, speed, weather, road_capacity

Usage:
    python data/kaggle_import.py --csv path/to/bangalore_routes1.csv
    python data/kaggle_import.py --download          # auto-downloads via Kaggle API
    python data/kaggle_import.py --download --limit 5000
"""

import argparse
import csv
import math
import os
import sys
import tempfile
import zipfile

import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host":     os.getenv("PGHOST",     "localhost"),
    "port":     int(os.getenv("PGPORT", "5432")),
    "dbname":   os.getenv("PGDATABASE", "traffic_db"),
    "user":     os.getenv("PGUSER",     "traffic_user"),
    "password": os.getenv("PGPASSWORD", "traffic_pass"),
}

DATASET_REF = "asshridattaaigal/bengaluru-traffic"
CSV_FILENAME = "bangalore_routes1.csv"

WEATHER_MAP = {
    "Clear": "Clear",
    "Rainy": "Rainy",
    "Foggy": "Foggy",
    "Cloudy": "Cloudy",
    "Stormy": "Stormy",
}

BATCH_SIZE = 500


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def download_csv(dest_dir):
    try:
        from kaggle.api.kaggle_api_extended import KaggleApiExtended
    except ImportError:
        print("ERROR: kaggle package not installed. Run: pip install kaggle")
        sys.exit(1)

    api = KaggleApiExtended()
    api.authenticate()
    print(f"Downloading {DATASET_REF} ...")
    api.dataset_download_files(DATASET_REF, path=dest_dir, unzip=True, quiet=False)
    csv_path = os.path.join(dest_dir, CSV_FILENAME)
    if not os.path.exists(csv_path):
        print(f"ERROR: Expected {CSV_FILENAME} in {dest_dir} after download.")
        sys.exit(1)
    print(f"Downloaded to {csv_path}")
    return csv_path


def load_junctions(conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT junction_id, junction_name, latitude, longitude FROM Junction")
        return cur.fetchall()


def load_roads(conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT road_id, zone_id FROM Road")
        return cur.fetchall()


def nearest_junction(lat, lon, junctions):
    best, best_dist = None, float("inf")
    for j in junctions:
        d = haversine(lat, lon, j["latitude"], j["longitude"])
        if d < best_dist:
            best_dist = d
            best = j
    return best


def congestion_from_vehicles_speed(vehicles, speed, road_capacity):
    ratio = vehicles / max(road_capacity, 1)
    if ratio >= 0.85 or speed < 15:
        return "SEVERE"
    elif ratio >= 0.65 or speed < 25:
        return "HIGH"
    elif ratio >= 0.40 or speed < 40:
        return "MODERATE"
    return "LOW"


def build_observation_time(hour, day_of_week):
    # Use a stable synthetic date so timestamps spread across a week
    day_offset = {"Weekday": 0, "Weekend": 5}.get(day_of_week, 0)
    return f"2026-10-{13 + day_offset:02d} {int(hour):02d}:00:00"


def import_csv(csv_path, conn, junctions, roads, limit):
    road_ids = [r["road_id"] for r in roads]

    insert_sql = """
        INSERT INTO Traffic_Observation
            (junction_id, road_id, observation_time, vehicle_count,
             avg_speed_kmph, congestion_level, weather_condition, data_source)
        VALUES %s
        ON CONFLICT DO NOTHING
    """

    batch = []
    inserted = 0
    skipped = 0

    print(f"Reading {csv_path} ...")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break

            try:
                lat = float(row["lat_src"])
                lon = float(row["lon_src"])
                vehicles = int(float(row["vehicles"]))
                speed = float(row["speed"])
                hour = row["hour"]
                day_of_week = row.get("day_of_week", "Weekday")
                weather_raw = row.get("weather", "Clear")
                road_capacity = int(float(row.get("road_capacity", "1000")))
            except (ValueError, KeyError):
                skipped += 1
                continue

            weather = WEATHER_MAP.get(weather_raw, "Clear")
            junction = nearest_junction(lat, lon, junctions)
            if junction is None:
                skipped += 1
                continue

            # Assign road from same zone as junction, cycling through available roads
            road_id = road_ids[(junction["junction_id"] + i) % len(road_ids)]
            obs_time = build_observation_time(hour, day_of_week)
            congestion = congestion_from_vehicles_speed(vehicles, speed, road_capacity)

            batch.append((
                junction["junction_id"],
                road_id,
                obs_time,
                vehicles,
                round(speed, 1),
                congestion,
                weather,
                "API",
            ))

            if len(batch) >= BATCH_SIZE:
                psycopg2.extras.execute_values(conn.cursor(), insert_sql, batch)
                conn.commit()
                inserted += len(batch)
                print(f"  Inserted {inserted} rows ...", end="\r")
                batch = []

        if batch:
            psycopg2.extras.execute_values(conn.cursor(), insert_sql, batch)
            conn.commit()
            inserted += len(batch)

    print(f"\nDone. Inserted: {inserted}  |  Skipped: {skipped}")
    return inserted


def main():
    parser = argparse.ArgumentParser(description="Import Kaggle Bengaluru traffic data")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", help="Path to bangalore_routes1.csv")
    group.add_argument("--download", action="store_true",
                       help="Auto-download from Kaggle API")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max rows to import (0 = all, default: all)")
    args = parser.parse_args()

    csv_path = args.csv
    if args.download:
        tmpdir = tempfile.mkdtemp(prefix="kaggle_traffic_")
        csv_path = download_csv(tmpdir)

    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)

    print("Connecting to database ...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print(f"ERROR: Cannot connect to database: {e}")
        sys.exit(1)

    junctions = load_junctions(conn)
    roads = load_roads(conn)
    print(f"Loaded {len(junctions)} junctions and {len(roads)} roads from database")

    if not junctions:
        print("ERROR: No junctions found. Run init_db.py first.")
        conn.close()
        sys.exit(1)

    limit = args.limit if args.limit > 0 else None
    import_csv(csv_path, conn, junctions, roads, limit)
    conn.close()


if __name__ == "__main__":
    main()
