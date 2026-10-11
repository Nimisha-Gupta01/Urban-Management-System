"""
tests/test_api.py — Pytest API tests for Urban Traffic Management System
BITS Pilani WILP | SESAP ZC337
Tests cover: CRUD endpoints, ACID transaction, role-based access, input validation
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app as flask_app, get_db
import sqlite3


# ── Test fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def db_path(tmp_path_factory):
    """Create a fresh in-memory-backed test DB."""
    tmp = tmp_path_factory.mktemp('data')
    db_file = str(tmp / 'test_traffic.db')
    flask_app.config['DB_PATH'] = db_file

    sql_dir = os.path.join(os.path.dirname(__file__), '..', 'sql')
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")

    for filename in ['schema.sql', 'seed_data.sql']:
        path = os.path.join(sql_dir, filename)
        with open(path) as f:
            conn.executescript(f.read())

    # Also apply DDL triggers/views (stop before transaction demos)
    triggers_path = os.path.join(sql_dir, 'triggers.sql')
    with open(triggers_path) as f:
        content = f.read()
    marker = '-- TRANSACTIONS'
    idx = content.find(marker)
    ddl_only = content[:idx] if idx != -1 else content
    conn.executescript(ddl_only)
    conn.commit()
    conn.close()
    return db_file


@pytest.fixture
def client(db_path):
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


# ── Helpers ───────────────────────────────────────────────────────────────────

def officer_headers():
    return {'X-User-Role': 'officer', 'Content-Type': 'application/json'}

def admin_headers():
    return {'X-User-Role': 'admin', 'Content-Type': 'application/json'}

def public_headers():
    return {'X-User-Role': 'public'}


# ── T1: Health check ──────────────────────────────────────────────────────────

def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


# ── T2: GET zones returns all 5 Bengaluru zones ───────────────────────────────

def test_get_zones(client):
    r = client.get('/api/zones')
    assert r.status_code == 200
    zones = r.get_json()
    assert len(zones) == 5
    names = {z['zone_name'] for z in zones}
    assert 'Whitefield' in names
    assert 'Koramangala' in names


# ── T3: GET roads returns non-empty list ─────────────────────────────────────

def test_get_roads(client):
    r = client.get('/api/roads')
    assert r.status_code == 200
    roads = r.get_json()
    assert len(roads) >= 10


# ── T4: GET roads filtered by zone ───────────────────────────────────────────

def test_get_roads_by_zone(client):
    r = client.get('/api/roads?zone_id=1')
    assert r.status_code == 200
    for road in r.get_json():
        assert road['zone_id'] == 1


# ── T5: GET junctions ────────────────────────────────────────────────────────

def test_get_junctions(client):
    r = client.get('/api/junctions')
    assert r.status_code == 200
    assert len(r.get_json()) >= 10


# ── T6: GET traffic observations ─────────────────────────────────────────────

def test_get_traffic(client):
    r = client.get('/api/traffic?hours=720')
    assert r.status_code == 200
    obs = r.get_json()
    assert len(obs) >= 50


# ── T7: POST traffic — officer role (ACID transaction) ───────────────────────

def test_post_traffic_officer(client):
    payload = {
        'junction_id': 1, 'road_id': 1,
        'vehicle_count': 220, 'avg_speed_kmph': 22.0,
        'congestion_level': 'HIGH', 'data_source': 'Sensor',
        'weather_condition': 'Clear'
    }
    r = client.post('/api/traffic', json=payload, headers={'X-User-Role': 'officer'})
    assert r.status_code == 201
    body = r.get_json()
    assert 'obs_id' in body
    assert body['obs_id'] > 0


# ── T8: POST traffic — public role is forbidden ───────────────────────────────

def test_post_traffic_forbidden_public(client):
    payload = {'junction_id': 1, 'road_id': 1, 'vehicle_count': 50,
               'avg_speed_kmph': 60, 'congestion_level': 'LOW', 'data_source': 'Manual'}
    r = client.post('/api/traffic', json=payload)  # no role header = public
    assert r.status_code == 403


# ── T9: POST traffic — missing required field returns 400 ────────────────────

def test_post_traffic_missing_field(client):
    payload = {'junction_id': 1, 'vehicle_count': 100}  # missing road_id etc.
    r = client.post('/api/traffic', json=payload, headers={'X-User-Role': 'officer'})
    assert r.status_code == 400
    assert 'Missing required fields' in r.get_json().get('error', '')


# ── T10: POST traffic — invalid FK triggers ROLLBACK ─────────────────────────

def test_post_traffic_invalid_junction(client):
    payload = {
        'junction_id': 9999, 'road_id': 1,
        'vehicle_count': 100, 'avg_speed_kmph': 40,
        'congestion_level': 'LOW', 'data_source': 'Manual'
    }
    r = client.post('/api/traffic', json=payload, headers={'X-User-Role': 'officer'})
    assert r.status_code == 400


# ── T11: GET incidents — open only ───────────────────────────────────────────

def test_get_open_incidents(client):
    r = client.get('/api/incidents?open_only=true')
    assert r.status_code == 200
    incidents = r.get_json()
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
    r = client.post('/api/incidents', json=payload, headers={'X-User-Role': 'officer'})
    assert r.status_code == 201
    assert 'incident_id' in r.get_json()


# ── T13: PUT incident — resolve ───────────────────────────────────────────────

def test_put_incident_resolve(client):
    # First create one
    post_r = client.post('/api/incidents',
                         json={'incident_type':'Breakdown','severity':'LOW','road_id':1},
                         headers={'X-User-Role': 'officer'})
    inc_id = post_r.get_json()['incident_id']

    r = client.put(f'/api/incidents/{inc_id}',
                   json={'resolved_datetime': '2026-10-11 18:00:00'},
                   headers={'X-User-Role': 'officer'})
    assert r.status_code == 200


# ── T14: PUT incident — resolved before reported should fail ─────────────────

def test_put_incident_invalid_resolution(client):
    post_r = client.post('/api/incidents',
                         json={'incident_type':'Accident','severity':'HIGH','road_id':1},
                         headers={'X-User-Role': 'officer'})
    inc_id = post_r.get_json()['incident_id']

    r = client.put(f'/api/incidents/{inc_id}',
                   json={'resolved_datetime': '2020-01-01 00:00:00'},
                   headers={'X-User-Role': 'officer'})
    assert r.status_code == 400


# ── T15: DELETE incident — admin only ────────────────────────────────────────

def test_delete_incident_admin(client):
    post_r = client.post('/api/incidents',
                         json={'incident_type':'Roadblock','severity':'LOW'},
                         headers={'X-User-Role': 'admin'})
    inc_id = post_r.get_json()['incident_id']

    r = client.delete(f'/api/incidents/{inc_id}', headers={'X-User-Role': 'admin'})
    assert r.status_code == 200

    # Confirm deleted
    r2 = client.get(f'/api/incidents/{inc_id}')
    assert r2.status_code == 404


# ── T16: DELETE incident — officer is forbidden ───────────────────────────────

def test_delete_incident_officer_forbidden(client):
    r = client.delete('/api/incidents/1', headers={'X-User-Role': 'officer'})
    assert r.status_code == 403


# ── T17: Dashboard endpoint returns expected structure ───────────────────────

def test_dashboard(client):
    r = client.get('/api/dashboard')
    assert r.status_code == 200
    body = r.get_json()
    assert 'junctions' in body
    assert 'zones' in body
    assert 'city_kpis' in body
    assert 'incident_summary' in body


# ── T18: Analytics endpoints ──────────────────────────────────────────────────

def test_analytics_peak_hours(client):
    r = client.get('/api/analytics/peak-hours')
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) <= 24  # at most 24 hour buckets


def test_analytics_top_congested(client):
    r = client.get('/api/analytics/top-congested')
    assert r.status_code == 200
    assert len(r.get_json()) <= 5


# ── T19: Audit log — admin only ──────────────────────────────────────────────

def test_audit_admin(client):
    r = client.get('/api/audit', headers={'X-User-Role': 'admin'})
    assert r.status_code == 200


def test_audit_public_forbidden(client):
    r = client.get('/api/audit')
    assert r.status_code == 403


# ── T20: HTML page routes return 200 ─────────────────────────────────────────

@pytest.mark.parametrize('path', ['/', '/traffic', '/incidents', '/observation', '/roads'])
def test_html_pages(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert b'Urban Traffic' in r.data
