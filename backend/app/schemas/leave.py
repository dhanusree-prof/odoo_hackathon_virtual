from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class LeaveCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str


class LeaveResponse(LeaveCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    status: str
    created_at: datetime


class LeaveStatusUpdate(BaseModel):
    status: str
