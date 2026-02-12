from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.database import engine
from app.models import domain

# Create all tables (useful before alembic is fully setup or for quick tests)
# domain.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResilienceOps Platform Backend")

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ready")
def readiness_check():
    return {"status": "ready"}

