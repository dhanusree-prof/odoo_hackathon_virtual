from typing import Annotated
from fastapi import APIRouter, Depends
from app.utils.dependencies import DbSession
from app.models.employee import Employee
from app.models.user import User
from app.schemas.payroll import PayrollCreate, PayrollResponse
from app.services import payroll
from app.utils.dependencies import current_user, require_roles

router = APIRouter()


@router.get("/", response_model=list[PayrollResponse])
def list_payroll(user: Annotated[User, Depends(current_user)], db: DbSession):
    employee = db.query(Employee).filter_by(user_id=user.id).first()
    return payroll.list_records(employee, db)


@router.post("/{employee_id}", response_model=PayrollResponse)
def create_payroll(employee_id: int, data: PayrollCreate, user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    employee = db.get(Employee, employee_id)
    if not employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee not found")
    return payroll.create_record(employee, data, db)
