"""API tests against a THROWAWAY PostgreSQL database: DATABASE_URL=... python -m pytest"""
import os
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from db import manage

pytestmark = pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set")
ALICE, BOB = {"X-Dev-User": "test-alice"}, {"X-Dev-User": "test-bob"}
ORIGIN = "http://localhost:5500"


@pytest.fixture(scope="module")
def client():
    manage.migrate()
    with manage.connect() as c:
        manage.seed(c)
    with TestClient(app) as cl:
        yield cl
    with manage.connect() as c:
        c.execute("DELETE FROM app.chat_sessions WHERE owner_id LIKE 'test-%'")


def err(r, status, code):
    assert r.status_code == status, r.text
    body = r.json()["error"]
    assert body["code"] == code and body["message"]
    return body


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "database": "ok", "version": "0.2.0"}


def test_list_patients_from_postgres(client):
    j = client.get("/api/patients").json()
    assert j["total"] == 10 and [p["patient_id"] for p in j["items"]] == [f"P-{i:03d}" for i in range(1, 11)]
    assert all(p["is_synthetic"] for p in j["items"])


def test_pagination(client):
    j = client.get("/api/patients?limit=3&offset=9").json()
    assert (len(j["items"]), j["total"], j["limit"], j["offset"]) == (1, 10, 3, 9)


@pytest.mark.parametrize("q", ["limit=0", "limit=101", "offset=-1", "limit=abc"])
def test_pagination_validation(client, q):
    body = err(client.get(f"/api/patients?{q}"), 422, "validation_error")
    assert body["details"][0]["field"].startswith("query.")


def test_patient_detail(client):
    j = client.get("/api/patients/P-001").json()
    assert j["patient_id"] == "P-001" and j["is_synthetic"] and j["primary_category"] == "alcohol"
    assert j["use"] and j["factors"] and j["interventions"] and j["progress"]
    assert [i["start_date"] for i in j["interventions"]] == sorted(i["start_date"] for i in j["interventions"])


@pytest.mark.parametrize("bad", ["abc", "p-001", "P-1", "P-0001"])
def test_malformed_patient_id(client, bad):
    for suffix in ("", "/history"):
        err(client.get(f"/api/patients/{bad}{suffix}"), 422, "validation_error")


def test_unknown_patient(client):
    err(client.get("/api/patients/P-999"), 404, "patient_not_found")
    err(client.get("/api/patients/P-999/history"), 404, "patient_not_found")


def test_history_is_chronological(client):
    j = client.get("/api/patients/P-001/history").json()
    dates = [i["event_date"] for i in j["items"]]
    assert j["total"] == 9 and dates == sorted(dates) and j["items"][0]["event_type"] == "onset"
    assert {i["source"] for i in j["items"]} == {"history", "progress"}
    assert len(client.get("/api/patients/P-001/history?limit=2&offset=8").json()["items"]) == 1


def test_papers(client):
    j = client.get("/api/papers").json()
    assert j["total"] == 4 and all(p["ingestion_status"] == "not_ingested" for p in j["items"])


def test_unknown_route_uses_error_envelope(client):
    err(client.get("/api/nope"), 404, "not_found")
    err(client.delete("/api/patients"), 405, "method_not_allowed")


def test_session_create_list_and_ownership(client):
    r = client.post("/api/sessions", json={"patient_id": "P-002", "mode": "rag", "title": "Cannabis case"}, headers=ALICE)
    assert r.status_code == 201
    s = r.json()
    assert s["patient_id"] == "P-002" and s["mode"] == "rag"
    assert [x["session_id"] for x in client.get("/api/sessions", headers=ALICE).json()["items"]] == [s["session_id"]]
    assert client.get("/api/sessions", headers=BOB).json()["total"] == 0
    assert client.get(f"/api/sessions/{s['session_id']}/messages", headers=ALICE).json()["total"] == 0
    err(client.get(f"/api/sessions/{s['session_id']}/messages", headers=BOB), 404, "session_not_found")


@pytest.mark.parametrize("body", [{"mode": "bogus"}, {"extra": 1}, {"title": ""}, {"title": "x" * 121}, {"patient_id": "bad"}])
def test_session_body_validation(client, body):
    err(client.post("/api/sessions", json=body, headers=ALICE), 422, "validation_error")


def test_session_unknown_patient_and_ids(client):
    err(client.post("/api/sessions", json={"patient_id": "P-999"}, headers=ALICE), 404, "patient_not_found")
    err(client.get("/api/sessions/not-a-uuid/messages", headers=ALICE), 422, "validation_error")
    err(client.get("/api/sessions/00000000-0000-0000-0000-000000000000/messages", headers=ALICE), 404, "session_not_found")
    err(client.get("/api/sessions", headers={"X-Dev-User": "bad user!"}), 422, "validation_error")


def test_dev_policy_disabled_outside_development(client, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    err(client.get("/api/sessions", headers=ALICE), 503, "auth_not_available")
    assert client.get("/api/patients").status_code == 200


def test_messages_paginated(client):
    sid = client.post("/api/sessions", json={}, headers=ALICE).json()["session_id"]
    with manage.connect() as c:
        for i in range(3):
            c.execute("INSERT INTO app.chat_messages (session_id, role, content) VALUES (%s,'user',%s)", (sid, f"m{i}"))
    j = client.get(f"/api/sessions/{sid}/messages?limit=2", headers=ALICE).json()
    assert j["total"] == 3 and [m["content"] for m in j["items"]] == ["m0", "m1"]
    assert [m["content"] for m in client.get(f"/api/sessions/{sid}/messages?limit=2&offset=2", headers=ALICE).json()["items"]] == ["m2"]


def test_cors_is_narrow(client):
    ok = client.get("/api/health", headers={"Origin": ORIGIN})
    assert ok.headers["access-control-allow-origin"] == ORIGIN
    assert "access-control-allow-origin" not in client.get("/api/health", headers={"Origin": "http://evil.example"}).headers
    pre = client.options("/api/sessions", headers={"Origin": ORIGIN, "Access-Control-Request-Method": "POST",
                                                   "Access-Control-Request-Headers": "content-type,x-dev-user"})
    assert pre.status_code == 200 and pre.headers["access-control-allow-origin"] == ORIGIN


def test_openapi_documents_endpoints_and_schemas(client):
    spec = client.get("/openapi.json").json()
    for path in ["/api/health", "/api/patients", "/api/patients/{patient_id}", "/api/patients/{patient_id}/history",
                 "/api/papers", "/api/sessions", "/api/sessions/{session_id}/messages"]:
        assert path in spec["paths"]
    assert {"post"} <= set(spec["paths"]["/api/sessions"])
    schemas = spec["components"]["schemas"]
    for name in ["PatientDetail", "PatientSummary", "HistoryItem", "PaperOut", "SessionCreate", "SessionOut", "MessageOut", "ErrorResponse"]:
        assert name in schemas
