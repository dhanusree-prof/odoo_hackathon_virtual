from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class PayrollCreate(BaseModel):
    period: str
    amount: Decimal
    payment_date: date | None = None


class PayrollResponse(PayrollCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    status: str


class PayrollStatusUpdate(BaseModel):
    status: str
