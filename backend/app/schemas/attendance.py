from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    work_date: date
    check_in: datetime | None
    check_out: datetime | None
    status: str
