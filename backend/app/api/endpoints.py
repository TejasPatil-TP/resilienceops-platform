from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import random

from app.core.database import get_db
from app.core.security import get_current_user, require_operator
from app.models import domain as models
from app.schemas import domain as schemas

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/services", response_model=schemas.Service)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db), current_user = Depends(require_operator)):
    db_service = models.Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("/services", response_model=List[schemas.Service])
def get_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Service).offset(skip).limit(limit).all()

@router.post("/slos", response_model=schemas.SLO)
def create_slo(slo: schemas.SLOCreate, db: Session = Depends(get_db), current_user = Depends(require_operator)):
    db_slo = models.SLO(**slo.dict())
    db.add(db_slo)
    db.commit()
    db.refresh(db_slo)
    return db_slo

@router.get("/slos", response_model=List[schemas.SLO])
def get_slos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.SLO).offset(skip).limit(limit).all()

@router.put("/slos/{slo_id}", response_model=schemas.SLO)
def update_slo(slo_id: int, slo: schemas.SLOCreate, db: Session = Depends(get_db)):
    db_slo = db.query(models.SLO).filter(models.SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    for var, value in vars(slo).items():
        setattr(db_slo, var, value)
    db.commit()
    db.refresh(db_slo)
    return db_slo

@router.delete("/slos/{slo_id}")
def delete_slo(slo_id: int, db: Session = Depends(get_db)):
    db_slo = db.query(models.SLO).filter(models.SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    db.delete(db_slo)
    db.commit()
    return {"ok": True}

@router.get("/slos/{slo_id}/evaluation")
def evaluate_slo(slo_id: int, good_events: int = 9990, total_events: int = 10000, db: Session = Depends(get_db)):
    db_slo = db.query(models.SLO).filter(models.SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    
    # Calculate SLI
    availability = (good_events / total_events) if total_events > 0 else 1.0
    
    # Target S
    s = db_slo.target_availability / 100.0
    
    # Allowed failure fraction = 1 - S
    allowed_failure = 1.0 - s
    
    # Consumed budget fraction = (1 - A) / (1 - S)
    if allowed_failure > 0:
        consumed_budget_fraction = (1.0 - availability) / allowed_failure
    else:
        consumed_budget_fraction = 0.0
        
    remaining_budget_fraction = 1.0 - consumed_budget_fraction

    return {
        "slo_id": slo_id,
        "availability_percentage": round(availability * 100, 2),
        "target_percentage": db_slo.target_availability,
        "consumed_budget_percentage": round(consumed_budget_fraction * 100, 2),
        "remaining_budget_percentage": round(remaining_budget_fraction * 100, 2),
        "status": "healthy" if remaining_budget_fraction > 0 else "at_risk"
    }

@router.post("/alerts", response_model=schemas.Alert)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    db_alert = models.Alert(**alert.dict(), status="active")
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/alerts", response_model=List[schemas.Alert])
def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Alert).offset(skip).limit(limit).all()

@router.put("/alerts/{alert_id}")
def update_alert_status(alert_id: int, status: str, db: Session = Depends(get_db)):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db_alert.status = status
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.post("/experiments", response_model=schemas.Experiment)
def create_experiment(exp: schemas.ExperimentCreate, db: Session = Depends(get_db), current_user = Depends(require_operator)):
    db_exp = models.Experiment(**exp.dict(), status="running")
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.get("/experiments", response_model=List[schemas.Experiment])
def get_experiments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Experiment).offset(skip).limit(limit).all()

@router.put("/experiments/{exp_id}")
def update_experiment_status(exp_id: int, status: str, db: Session = Depends(get_db)):
    db_exp = db.query(models.Experiment).filter(models.Experiment.id == exp_id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db_exp.status = status
    if status in ("completed", "cancelled"):
        db_exp.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_exp)
    return db_exp

