import asyncio
import random
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Response, Depends, Header
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import logging
import uuid
from datetime import datetime, timezone

# Application state for fault injection
class AppState:
    def __init__(self):
        self.latency_ms: int = 0
        self.error_rate: float = 0.0
        self.lock = asyncio.Lock()
        self.current_experiment_id: Optional[str] = None

app_state = AppState()

app = FastAPI(title="Demo Service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"])
ERROR_COUNT = Counter("http_errors_total", "Total HTTP errors", ["method", "endpoint"])

@app.middleware("http")
async def metrics_and_fault_injection(request: Request, call_next):
    if request.url.path in ["/health", "/ready", "/metrics"] or request.url.path.startswith("/api/experiments") or request.url.path == "/":
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
        REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(process_time)
        return response

    start_time = time.time()
    
    allowed_targets = ["/api/orders"]
    is_allowed = any(request.url.path.startswith(t) for t in allowed_targets)
    if not is_allowed:
        try:
            response = await call_next(request)
        except Exception as e:
            ERROR_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
            raise e
        process_time = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
        REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(process_time)
        return response

    # Safely snapshot state
    latency = 0
    err_rate = 0.0
    async with app_state.lock:
        latency = app_state.latency_ms
        err_rate = app_state.error_rate

    if err_rate > 0:
        if random.random() < err_rate:
            ERROR_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
            REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=500).inc()
            return Response(status_code=500, content="Injected Error")

    if latency > 0:
        await asyncio.sleep(latency / 1000.0)

    try:
        response = await call_next(request)
    except Exception as e:
        ERROR_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        raise e

    process_time = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
    REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(process_time)
    return response

class Order(BaseModel):
    id: str
    item: str
    quantity: int

class LatencyExperiment(BaseModel):
    latency_ms: int
    duration_s: Optional[int] = None

class ErrorExperiment(BaseModel):
    error_rate: float
    duration_s: Optional[int] = None

MOCK_ORDERS = {
    "1": Order(id="1", item="Laptop", quantity=1),
    "2": Order(id="2", item="Mouse", quantity=2),
}

@app.get("/")
def read_root():
    return {"name": "demo-service", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/orders")
def get_orders():
    return list(MOCK_ORDERS.values())

@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    order = MOCK_ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

API_KEY = os.getenv("EXPERIMENT_API_KEY")
if not API_KEY and os.getenv("ENVIRONMENT", "development") == "production":
    raise RuntimeError("EXPERIMENT_API_KEY environment variable is required in production")
if not API_KEY:
    API_KEY = "demo-secret-key"

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/api/experiments/latency", dependencies=[Depends(verify_api_key)])
async def inject_latency(exp: LatencyExperiment):
    if exp.duration_s is not None and (exp.duration_s <= 0 or exp.duration_s > 3600):
        raise HTTPException(status_code=422, detail="Duration must be between 1 and 3600 seconds")
    if exp.latency_ms < 0 or exp.latency_ms > 5000:
        raise HTTPException(status_code=422, detail="Latency must be between 0 and 5000 ms")
    
    exp_id = str(uuid.uuid4())
    async with app_state.lock:
        app_state.latency_ms = exp.latency_ms
        app_state.current_experiment_id = exp_id
    
    logger.info(f"AUDIT [{datetime.now(timezone.utc).isoformat()}]: id={exp_id} action=create_latency outcome=success target=/api/orders latency_ms={exp.latency_ms}")
    if exp.duration_s:
        asyncio.create_task(expire_experiment(exp_id, exp.duration_s))
    return {"message": f"Latency injected: {exp.latency_ms} ms"}

@app.post("/api/experiments/error", dependencies=[Depends(verify_api_key)])
async def inject_error(exp: ErrorExperiment):
    if exp.duration_s is not None and (exp.duration_s <= 0 or exp.duration_s > 3600):
        raise HTTPException(status_code=422, detail="Duration must be between 1 and 3600 seconds")
    if exp.error_rate < 0.0 or exp.error_rate > 1.0:
        raise HTTPException(status_code=422, detail="Error rate must be between 0.0 and 1.0")
    
    exp_id = str(uuid.uuid4())
    async with app_state.lock:
        app_state.error_rate = exp.error_rate
        app_state.current_experiment_id = exp_id

    logger.info(f"AUDIT [{datetime.now(timezone.utc).isoformat()}]: id={exp_id} action=create_error outcome=success target=/api/orders error_rate={exp.error_rate}")
    if exp.duration_s:
        asyncio.create_task(expire_experiment(exp_id, exp.duration_s))
    return {"message": f"Error rate injected: {exp.error_rate}"}

@app.delete("/api/experiments", dependencies=[Depends(verify_api_key)])
async def reset_experiments():
    async with app_state.lock:
        exp_id = app_state.current_experiment_id or 'none'
        app_state.latency_ms = 0
        app_state.error_rate = 0.0
        app_state.current_experiment_id = None
    logger.info(f"AUDIT [{datetime.now(timezone.utc).isoformat()}]: id={exp_id} action=kill_switch outcome=success baseline=restored")
    return {"message": "Experiments reset"}

async def expire_experiment(exp_id: str, duration: int):
    await asyncio.sleep(duration)
    async with app_state.lock:
        if app_state.current_experiment_id == exp_id:
            app_state.latency_ms = 0
            app_state.error_rate = 0.0
            app_state.current_experiment_id = None
            logger.info(f"AUDIT [{datetime.now(timezone.utc).isoformat()}]: id={exp_id} action=auto_expiry outcome=success baseline=restored")
