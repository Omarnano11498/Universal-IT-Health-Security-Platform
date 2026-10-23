from fastapi.testclient import TestClient
import app.server as server
from app.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_has_language_selector():
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="lang"' in response.text
    assert 'id="run-scan"' in response.text
    assert 'id="filter"' in response.text
    assert 'fetch("/api/scan"' in response.text


def test_scan_endpoint_saves_results(monkeypatch):
    scan = {"scan_id": "test-scan", "findings": [], "summary": {}}
    monkeypatch.setattr(server, "run_scan", lambda: scan)

    response = client.post("/api/scan")
    assert response.status_code == 200
    assert response.json()["data"] == scan
    assert client.get("/api/scan/results").json()["data"] == scan
