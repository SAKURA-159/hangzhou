"""Typed HTTP client for the backend API."""

import os
from typing import Any

import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def _headers() -> dict[str, str]:
    h = {}
    token = st.session_state.get("access_token")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get(path: str, params: dict | None = None) -> dict:
    resp = requests.get(f"{API_BASE}{path}", params=params, headers=_headers(), timeout=30)
    return _handle(resp)


def _post(path: str, json: dict | None = None, files: Any = None) -> dict:
    resp = requests.post(f"{API_BASE}{path}", json=json, files=files, headers=_headers(), timeout=30)
    return _handle(resp)


def _put(path: str, json: dict) -> dict:
    resp = requests.put(f"{API_BASE}{path}", json=json, headers=_headers(), timeout=30)
    return _handle(resp)


def _delete(path: str) -> dict:
    resp = requests.delete(f"{API_BASE}{path}", headers=_headers(), timeout=30)
    return _handle(resp)


def _handle(resp: requests.Response) -> dict:
    if resp.status_code == 401:
        st.session_state.clear()
        st.rerun()
    if resp.status_code >= 400:
        detail = resp.json().get("detail", resp.text) if resp.text else "Request failed"
        st.error(f"Error {resp.status_code}: {detail}")
        return {}
    return resp.json()


# ---------------- Auth ----------------

def login(username: str, password: str) -> dict:
    payload = {"username": username, "password": password}
    resp = requests.post(f"{API_BASE}/api/auth/login", json=payload, timeout=30)
    if resp.status_code >= 400:
        raise ValueError(resp.json().get("detail", "Login failed"))
    return resp.json()


def register(username: str, email: str, password: str) -> dict:
    resp = requests.post(
        f"{API_BASE}/api/auth/register",
        json={"username": username, "email": email, "password": password},
        timeout=30,
    )
    if resp.status_code >= 400:
        raise ValueError(resp.json().get("detail", "Registration failed"))
    return resp.json()


# ---------------- Houses ----------------

def get_houses(filters: dict | None = None) -> dict:
    return _get("/api/houses", params=filters or {})


def get_house(house_id: int) -> dict:
    return _get(f"/api/houses/{house_id}")


def create_house(data: dict) -> dict:
    return _post("/api/houses", json=data)


def update_house(house_id: int, data: dict) -> dict:
    return _put(f"/api/houses/{house_id}", json=data)


def delete_house(house_id: int) -> dict:
    return _delete(f"/api/houses/{house_id}")


# ---------------- Stats ----------------

def get_region_stats(filters: dict | None = None) -> dict:
    return _get("/api/stats/regions", params=filters or {})


def get_overview_stats(filters: dict | None = None) -> dict:
    return _get("/api/stats/overview", params=filters or {})


# ---------------- Import ----------------

def import_csv(file_bytes: bytes, filename: str) -> dict:
    return _post("/api/import/csv", files={"file": (filename, file_bytes, "text/csv")})
