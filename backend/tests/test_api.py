from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
auth_client = TestClient(app, headers={"Authorization": "Bearer dev-token"})

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200

def test_unauthenticated_access():
    response = client.get("/api/v1/services")
    assert response.status_code == 401

def test_invalid_token():
    invalid_client = TestClient(app, headers={"Authorization": "Bearer invalid-token"})
    response = invalid_client.get("/api/v1/services")
    assert response.status_code == 401

def test_create_and_get_service():
    response = auth_client.post("/api/v1/services", json={"name": "test-service", "version": "1.0"})
    assert response.status_code == 200
    service_id = response.json()["id"]

    res_get = auth_client.get("/api/v1/services")
    assert res_get.status_code == 200
    assert len(res_get.json()) > 0

def test_create_slo():
    res_svc = auth_client.post("/api/v1/services", json={"name": "test-service", "version": "1.0"})
    svc_id = res_svc.json()["id"]

    response = auth_client.post("/api/v1/slos", json={
        "service_id": svc_id, "name": "Availability SLO",
        "description": "Ensure 99.9% availability", "target_availability": 99.9, "window_days": 30
    })
    assert response.status_code == 200
    slo_id = response.json()["id"]
    
    res_eval = auth_client.get(f"/api/v1/slos/{slo_id}/evaluation")
    assert res_eval.status_code == 200

def test_create_and_ack_alert():
    res_svc = auth_client.post("/api/v1/services", json={"name": "test-service-alert", "version": "1.0"})
    svc_id = res_svc.json()["id"]

    res_alert = auth_client.post("/api/v1/alerts", json={
        "service_id": svc_id, "severity": "critical", "message": "High CPU usage"
    })
    assert res_alert.status_code == 200
    alert_id = res_alert.json()["id"]

    res_put = auth_client.put(f"/api/v1/alerts/{alert_id}?status=resolved")
    assert res_put.status_code == 200

def test_experiment():
    res_svc = auth_client.post("/api/v1/services", json={"name": "test-service-exp", "version": "1.0"})
    svc_id = res_svc.json()["id"]

    res_exp = auth_client.post("/api/v1/experiments", json={
        "service_id": svc_id, "type": "chaos-cpu", "parameters": "{\"cpu_load\": 80}"
    })
    assert res_exp.status_code == 200
    exp_id = res_exp.json()["id"]

    res_put = auth_client.put(f"/api/v1/experiments/{exp_id}?status=completed")
    assert res_put.status_code == 200
