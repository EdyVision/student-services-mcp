from datetime import datetime
from pydantic import BaseModel


class Status(BaseModel):
    status: str


class Health(BaseModel):
    # storage: Status
    docs: Status


class HealthResult(BaseModel):
    app_name: str
    version: str
    system_time: datetime
    health: Health


class HealthResponse(BaseModel):
    message: HealthResult
