"""
tests/test_api.py — Pytest API tests for Urban Traffic Management System
BITS Pilani WILP | SESAP ZC337
Tests cover: CRUD endpoints, ACID transaction, role-based access, input validation
Uses FastAPI TestClient + psycopg2 against a real PostgreSQL test database.
"""

import pytest
import os
import psycopg2
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, DB_CONFIG

# ── Test fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    """Init schema + seed data into the test PostgreSQL DB once per session."""
    sql_dir = os.path.join(os.path.dirname(__file__), '..', 'sql')
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True

    def run(path):
        with open(path) as f:
            content = f.read()
        with conn.cursor() as cur:
            cur.execute(content)

    # Drop everything and recreate
    with conn.cursor() as cur:
        cur.execute("""
            DO $$ DECLARE r RECORD; BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname='public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS '||quote_ident(r.tablename)||' CASCADE';
                END LOOP;
                FOR r IN (SELECT viewname FROM pg_views WHERE schemaname='public') LOOP
                    EXECUTE 'DROP VIEW IF EXISTS '||quote_ident(r.viewname)||' CASCADE';
                END LOOP;
            END $$;
        """)

    run(os.path.join(sql_dir, 'schema.sql'))

    # Triggers: DDL only (stop before transaction demos)
    with open(os.path.join(sql_dir, 'triggers.sql')) as f:
        content = f.read()
    marker = '-- TRANSACTIONS — ACID DEMONSTRATION'
    idx = content.find(marker)
    ddl_only = content[:idx] if idx != -1 else content
    # Strip CHECKPOINT line (requires superuser in some configs)
    ddl_only = '\n'.join(l for l in ddl_only.splitlines() if not l.strip().startswith('CHECKPOINT'))
    with conn.cursor() as cur:
        cur.execute(ddl_only)

    run(os.path.join(sql_dir, 'seed_data.sql'))
    conn.close()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ── Helpers ───────────────────────────────────────────────────────────────────

def officer_headers():
    return {'X-User-Role': 'officer'}

def admin_headers():
    return {'X-User-Role': 'admin'}

def public_headers():
    return {'X-User-Role': 'public'}


# ── T1: Health check ──────────────────────────────────────────────────────────

def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


# ── T2: GET zones returns all 5 Bengaluru zones ───────────────────────────────

def test_get_zones(client):
    r = client.get('/api/zones')
    assert r.status_code == 200
    zones = r.json()
    assert len(zones) == 5
    names = {z['zone_name'] for z in zones}
    assert 'Whitefield' in names
    assert 'Koramangala' in names


# ── T3: GET roads returns non-empty list ─────────────────────────────────────

def test_get_roads(client):
    r = client.get('/api/roads')
    assert r.status_code == 200
    assert len(r.json()) >= 10


# ── T4: GET roads filtered by zone ───────────────────────────────────────────

def test_get_roads_by_zone(client):
    r = client.get('/api/roads?zone_id=1')
    assert r.status_code == 200
    for road in r.json():
        assert road['zone_id'] == 1


# ── T5: GET junctions ────────────────────────────────────────────────────────

def test_get_junctions(client):
    r = client.get('/api/junctions')
    assert r.status_code == 200
    assert len(r.json()) >= 10


# ── T6: GET traffic observations ─────────────────────────────────────────────

def test_get_traffic(client):
    r = client.get('/api/traffic?hours=720')
    assert r.status_code == 200
    assert len(r.json()) >= 50


# ── T7: POST traffic — officer role (ACID transaction) ───────────────────────

def test_post_traffic_officer(client):
    payload = {
        'junction_id': 1, 'road_id': 1,
        'vehicle_count': 220, 'avg_speed_kmph': 22.0,
        'congestion_level': 'HIGH', 'data_source': 'Sensor',
        'weather_condition': 'Clear'
    }
    r = client.post('/api/traffic', json=payload, headers=officer_headers())
    assert r.status_code == 201
    body = r.json()
    assert 'obs_id' in body
    assert body['obs_id'] > 0


# ── T8: POST traffic — public role is forbidden ───────────────────────────────

def test_post_traffic_forbidden_public(client):
    payload = {'junction_id': 1, 'road_id': 1, 'vehicle_count': 50,
               'avg_speed_kmph': 60, 'congestion_level': 'LOW', 'data_source': 'Manual'}
    r = client.post('/api/traffic', json=payload)
    assert r.status_code == 403


# ── T9: POST traffic — missing required field returns 422 ────────────────────

def test_post_traffic_missing_field(client):
    payload = {'junction_id': 1, 'vehicle_count': 100}  # missing road_id etc.
    r = client.post('/api/traffic', json=payload, headers=officer_headers())
    assert r.status_code == 422  # FastAPI validation error


# ── T10: POST traffic — invalid FK triggers ROLLBACK ─────────────────────────

def test_post_traffic_invalid_junction(client):
    payload = {
        'junction_id': 9999, 'road_id': 1,
        'vehicle_count': 100, 'avg_speed_kmph': 40,
        'congestion_level': 'LOW', 'data_source': 'Manual'
    }
    r = client.post('/api/traffic', json=payload, headers=officer_headers())
    assert r.status_code == 400


# ── T11: GET incidents — open only ───────────────────────────────────────────

def test_get_open_incidents(client):
    r = client.get('/api/incidents?open_only=true')
    assert r.status_code == 200
    incidents = r.json()
    for i in incidents:
        assert i['resolved_datetime'] is None


# ── T12: POST incident ────────────────────────────────────────────────────────

def test_post_incident(client):
    payload = {
        'incident_type': 'Flooding',
        'severity': 'MEDIUM',
        'description': 'Waterlogging on test road',
        'road_id': 2,
        'reported_by': 'Test Officer'
    }
    r = client.post('/api/incidents', json=payload, headers=officer_headers())
    assert r.status_code == 201
    assert 'incident_id' in r.json()


# ── T13: PUT incident — resolve ───────────────────────────────────────────────

def test_put_incident_resolve(client):
    post_r = client.post('/api/incidents',
                         json={'incident_type': 'Breakdown', 'severity': 'LOW', 'road_id': 1},
                         headers=officer_headers())
    inc_id = post_r.json()['incident_id']

    r = client.put(f'/api/incidents/{inc_id}',
                   json={'resolved_datetime': '2026-10-18 18:00:00'},
                   headers=officer_headers())
    assert r.status_code == 200


# ── T14: PUT incident — resolved before reported should fail ─────────────────

def test_put_incident_invalid_resolution(client):
    post_r = client.post('/api/incidents',
                         json={'incident_type': 'Accident', 'severity': 'HIGH', 'road_id': 1},
                         headers=officer_headers())
    inc_id = post_r.json()['incident_id']

    r = client.put(f'/api/incidents/{inc_id}',
                   json={'resolved_datetime': '2020-01-01 00:00:00'},
                   headers=officer_headers())
    assert r.status_code == 400


# ── T15: DELETE incident — admin only ────────────────────────────────────────

def test_delete_incident_admin(client):
    post_r = client.post('/api/incidents',
                         json={'incident_type': 'Roadblock', 'severity': 'LOW'},
                         headers=admin_headers())
    inc_id = post_r.json()['incident_id']

    r = client.delete(f'/api/incidents/{inc_id}', headers=admin_headers())
    assert r.status_code == 200

    r2 = client.get(f'/api/incidents/{inc_id}')
    assert r2.status_code == 404


# ── T16: DELETE incident — officer is forbidden ───────────────────────────────

def test_delete_incident_officer_forbidden(client):
    r = client.delete('/api/incidents/1', headers=officer_headers())
    assert r.status_code == 403


# ── T17: Dashboard endpoint returns expected structure ───────────────────────

def test_dashboard(client):
    r = client.get('/api/dashboard')
    assert r.status_code == 200
    body = r.json()
    assert 'junctions' in body
    assert 'zones' in body
    assert 'city_kpis' in body
    assert 'incident_summary' in body


def test_map_data(client):
    r = client.get('/api/map')
    assert r.status_code == 200
    body = r.json()
    assert 'junctions' in body
    assert 'incidents' in body
    for j in body['junctions']:
        assert j['latitude'] is not None
        assert j['longitude'] is not None


# ── T18: Analytics endpoints ──────────────────────────────────────────────────

def test_analytics_peak_hours(client):
    r = client.get('/api/analytics/peak-hours')
    assert r.status_code == 200
    assert len(r.json()) <= 24


def test_analytics_top_congested(client):
    r = client.get('/api/analytics/top-congested')
    assert r.status_code == 200
    assert len(r.json()) <= 5


# ── T19: Audit log — admin only ──────────────────────────────────────────────

def test_audit_admin(client):
    r = client.get('/api/audit', headers=admin_headers())
    assert r.status_code == 200


def test_audit_public_forbidden(client):
    r = client.get('/api/audit')
    assert r.status_code == 403
