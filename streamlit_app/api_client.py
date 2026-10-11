"""Shared API client for Streamlit pages."""
import os
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

ROLE_HEADERS = {
    "public":  {"X-User-Role": "public"},
    "officer": {"X-User-Role": "officer"},
    "admin":   {"X-User-Role": "admin"},
}


def headers(role="public"):
    return ROLE_HEADERS.get(role, ROLE_HEADERS["public"])


def get(path, params=None, role="public"):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, headers=headers(role), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server. Make sure FastAPI is running on port 8000."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def post(path, data, role="public"):
    try:
        r = requests.post(f"{API_BASE}{path}", json=data, headers=headers(role), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def put(path, data, role="public"):
    try:
        r = requests.put(f"{API_BASE}{path}", json=data, headers=headers(role), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def delete(path, role="public"):
    try:
        r = requests.delete(f"{API_BASE}{path}", headers=headers(role), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API server."
    except requests.exceptions.HTTPError as e:
        return None, f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)
