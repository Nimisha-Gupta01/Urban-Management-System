"""
data/simulator.py
Traffic sensor simulator — runs as a separate Docker service.
POSTs a realistic traffic observation to POST /api/traffic every 30 seconds.
Also writes a raw Sensor_Reading via POST /api/sensors/reading.
Rush-hour pattern: high traffic 8-10am and 5-8pm, low at night.
"""

import os
import time
import random
import logging
from datetime import datetime

import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
INTERVAL_SEC = 30
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

WEATHER_OPTIONS = ["Clear", "Rainy", "Foggy", "Cloudy", "Stormy"]
WEATHER_WEIGHTS = [0.60, 0.20, 0.05, 0.10, 0.05]


def get_junctions() -> list:
    try:
        resp = requests.get(f"{API_BASE}/api/junctions", timeout=10)
        resp.raise_for_status()
        junctions = resp.json()
        return [j for j in junctions if j.get("junction_id")]
    except Exception as e:
        log.warning(f"Could not fetch junctions: {e}")
        return []


def get_sensors() -> list:
    try:
        resp = requests.get(f"{API_BASE}/api/sensors", timeout=10)
        resp.raise_for_status()
        sensors = resp.json()
        return [s["sensor_id"] for s in sensors if s.get("sensor_id")]
    except Exception:
        return []


def get_road_for_junction(junction_id: int):
    try:
        resp = requests.get(f"{API_BASE}/api/roads", timeout=10)
        resp.raise_for_status()
        roads = resp.json()
        if roads:
            return random.choice(roads)["road_id"]
    except Exception:
        pass
    return None


def traffic_profile(hour: int):
    if 8 <= hour < 10 or 17 <= hour < 20:
        vehicle_count = random.randint(180, 320)
        avg_speed = round(random.uniform(8, 25), 1)
        congestion_level = random.choice(["HIGH", "SEVERE", "SEVERE"])
    elif 10 <= hour < 17:
        vehicle_count = random.randint(80, 160)
        avg_speed = round(random.uniform(25, 50), 1)
        congestion_level = random.choice(["MODERATE", "MODERATE", "HIGH"])
    elif 20 <= hour < 22:
        vehicle_count = random.randint(60, 120)
        avg_speed = round(random.uniform(35, 55), 1)
        congestion_level = random.choice(["LOW", "MODERATE"])
    else:
        vehicle_count = random.randint(5, 50)
        avg_speed = round(random.uniform(50, 75), 1)
        congestion_level = "LOW"
    return vehicle_count, avg_speed, congestion_level


def post_observation(junction_id, road_id, vehicle_count, avg_speed, congestion_level, weather):
    payload = {
        "junction_id": junction_id,
        "road_id": road_id,
        "vehicle_count": vehicle_count,
        "avg_speed_kmph": avg_speed,
        "congestion_level": congestion_level,
        "data_source": "Sensor",
        "weather_condition": weather,
    }
    try:
        resp = requests.post(
            f"{API_BASE}/api/traffic",
            json=payload,
            headers={"X-User-Role": "officer"},
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        log.warning(f"POST /api/traffic failed: {e}")
        return False


def post_sensor_reading(sensor_id, vehicle_count, avg_speed):
    payload = {
        "sensor_id": sensor_id,
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
        "raw_payload": {"source": "simulator", "sensor_id": sensor_id},
    }
    try:
        resp = requests.post(f"{API_BASE}/api/sensors/reading", json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        log.warning(f"           ⚠️  Sensor reading failed (sensor_id={sensor_id}): {e}")
        return False


def wait_for_api(max_retries=20, delay=5):
    for i in range(max_retries):
        try:
            resp = requests.get(f"{API_BASE}/api/health", timeout=5)
            if resp.status_code == 200:
                log.info("API is ready.")
                return True
        except Exception:
            pass
        log.info(f"Waiting for API... ({i+1}/{max_retries})")
        time.sleep(delay)
    return False


def main():
    if not wait_for_api():
        log.error("API never became ready. Exiting.")
        return

    log.info("=" * 60)
    log.info("  UTMS Traffic Simulator — started")
    log.info(f"  Posting to: {API_BASE}  |  Interval: {INTERVAL_SEC}s")
    log.info("=" * 60)

    sensor_ids = get_sensors()
    log.info(f"  Loaded {len(sensor_ids)} sensors from database")

    tick = 0
    while True:
        tick += 1
        junctions = get_junctions()
        if not junctions:
            log.warning("No junctions found, retrying in 30s...")
            time.sleep(INTERVAL_SEC)
            continue

        junction = random.choice(junctions)
        junction_id = junction["junction_id"]
        road_id = get_road_for_junction(junction_id)
        if road_id is None:
            time.sleep(INTERVAL_SEC)
            continue

        hour = datetime.now().hour
        vehicle_count, avg_speed, congestion_level = traffic_profile(hour)
        weather = random.choices(WEATHER_OPTIONS, weights=WEATHER_WEIGHTS)[0]

        LEVEL_ICON = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "SEVERE": "🔴"}
        icon = LEVEL_ICON.get(congestion_level, "⚪")

        ok = post_observation(junction_id, road_id, vehicle_count,
                              avg_speed, congestion_level, weather)
        if ok:
            log.info(
                f"[Tick #{tick:04d}] {icon} {congestion_level:<8} | "
                f"{junction.get('junction_name', junction_id):<35} | "
                f"Vehicles: {vehicle_count:>3} | Speed: {avg_speed:>5} km/h | Weather: {weather}"
            )

        if sensor_ids:
            sensor_id = random.choice(sensor_ids)
            posted = post_sensor_reading(
                sensor_id=sensor_id,
                vehicle_count=vehicle_count,
                avg_speed=avg_speed,
            )
            if posted:
                log.info(
                    f"           📡 Sensor #{sensor_id} reading saved "
                    f"(vehicles={vehicle_count}, speed={avg_speed})"
                )

        time.sleep(INTERVAL_SEC)



if __name__ == "__main__":
    main()
