from fastapi.testclient import TestClient

from agentic_sdlc.api import app


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_endpoint():
    response = TestClient(app).post("/v1/runs", json={
        "requirement": "Build a scalable URL shortener service with APIs, persistence, and analytics.",
        "approve": False,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["validation"]["passed"] is True
    assert body["approval_status"] == "awaiting_human_approval"
