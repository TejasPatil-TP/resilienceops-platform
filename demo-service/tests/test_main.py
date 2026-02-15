import time
import pytest
import asyncio
from fastapi.testclient import TestClient

from app.main import app, app_state

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    # Because endpoints run async and modify app_state, we can just hit the DELETE endpoint
    client.delete("/api/experiments", headers={"x-api-key": "demo-secret-key"})
    yield
    client.delete("/api/experiments", headers={"x-api-key": "demo-secret-key"})

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200

def test_get_orders():
    response = client.get("/api/orders")
    assert response.status_code == 200

def test_get_order():
    response = client.get("/api/orders/1")
    assert response.status_code == 200

def test_get_order_not_found():
    response = client.get("/api/orders/999")
    assert response.status_code == 404

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

def test_latency_injection():
    response = client.post("/api/experiments/latency", json={"latency_ms": 100}, headers={"x-api-key": "demo-secret-key"})
    assert response.status_code == 200
    
    start_time = time.time()
    response = client.get("/api/orders")
    duration = time.time() - start_time
    assert response.status_code == 200
    assert duration >= 0.1
    
    client.delete("/api/experiments", headers={"x-api-key": "demo-secret-key"})
    
    start_time = time.time()
    client.get("/api/orders")
    duration = time.time() - start_time
    assert duration < 0.1

def test_latency_validation():
    response = client.post("/api/experiments/latency", json={"latency_ms": 6000}, headers={"x-api-key": "demo-secret-key"})
    assert response.status_code == 422
    response = client.post("/api/experiments/latency", json={"latency_ms": 100, "duration_s": 4000}, headers={"x-api-key": "demo-secret-key"})
    assert response.status_code == 422

def test_error_injection():
    response = client.post("/api/experiments/error", json={"error_rate": 1.0}, headers={"x-api-key": "demo-secret-key"})
    assert response.status_code == 200
    
    response = client.get("/api/orders")
    assert response.status_code == 500
    
    client.delete("/api/experiments", headers={"x-api-key": "demo-secret-key"})
    assert client.get("/api/orders").status_code == 200

def test_error_validation():
    response = client.post("/api/experiments/error", json={"error_rate": 1.5}, headers={"x-api-key": "demo-secret-key"})
    assert response.status_code == 422

def test_unauthorized():
    assert client.post("/api/experiments/error", json={"error_rate": 1.0}).status_code == 401
    assert client.post("/api/experiments/latency", json={"latency_ms": 100}).status_code == 401
    assert client.delete("/api/experiments").status_code == 401

def test_automatic_expiry_and_overlapping():
    async def run_test():
        from app.main import expire_experiment, app_state
        import uuid
        
        # Inject first
        response1 = client.post("/api/experiments/latency", json={"latency_ms": 100}, headers={"x-api-key": "demo-secret-key"})
        assert response1.status_code == 200
        
        async with app_state.lock:
            exp1_id = app_state.current_experiment_id
            
        # Inject second (overlaps and overrides first)
        response2 = client.post("/api/experiments/latency", json={"latency_ms": 200}, headers={"x-api-key": "demo-secret-key"})
        assert response2.status_code == 200
        
        async with app_state.lock:
            exp2_id = app_state.current_experiment_id
            
        assert exp1_id != exp2_id
        
        # Manually trigger the expire for exp1 (simulating timer firing)
        await expire_experiment(exp1_id, 0)
        
        # State should NOT be reset because exp2 is active
        async with app_state.lock:
            assert app_state.latency_ms == 200
            
        # Trigger expire for exp2
        await expire_experiment(exp2_id, 0)
        
        # State SHOULD be reset
        async with app_state.lock:
            assert app_state.latency_ms == 0
            
    asyncio.run(run_test())

def test_missing_api_key_in_production(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.delenv('EXPERIMENT_API_KEY', raising=False)
    
    from prometheus_client import REGISTRY
    REGISTRY._collector_to_names.clear()
    REGISTRY._names_to_collectors.clear()
    
    import importlib
    import app.main as demo_main
    
    import pytest
    with pytest.raises(RuntimeError, match="EXPERIMENT_API_KEY environment variable is required in production"):
        importlib.reload(demo_main)
