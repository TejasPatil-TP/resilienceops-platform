from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    version: str

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class SLOBase(BaseModel):
    service_id: int
    name: str
    description: str
    target_availability: float
    window_days: int

class SLOCreate(SLOBase):
    pass

class SLO(SLOBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class ExperimentBase(BaseModel):
    service_id: int
    type: str
    parameters: str

class ExperimentCreate(ExperimentBase):
    pass

class Experiment(ExperimentBase):
    id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    class Config:
        orm_mode = True
        from_attributes = True

class AlertBase(BaseModel):
    service_id: int
    severity: str
    message: str

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    status: str
    timestamp: datetime
    class Config:
        orm_mode = True
        from_attributes = True
