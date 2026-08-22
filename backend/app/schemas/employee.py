from pydantic import BaseModel, ConfigDict


class EmployeeCreate(BaseModel):
    full_name: str
    department: str = "General"
    job_title: str = "Employee"
    phone: str | None = None


class EmployeeResponse(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
