from typing import Annotated
from fastapi import APIRouter, Depends
from app.utils.dependencies import DbSession
from app.models.employee import Employee
from app.models.user import User
from app.schemas.payroll import PayrollCreate, PayrollResponse, PayrollStatusUpdate
from app.services import payroll
from app.utils.dependencies import current_user, require_roles

router = APIRouter()


@router.get("/admin/all", response_model=list[PayrollResponse])
def list_all_payroll(user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    return payroll.list_all(db)


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


@router.patch("/{payroll_id}/status", response_model=PayrollResponse)
def update_payroll_status(payroll_id: int, data: PayrollStatusUpdate, user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    return payroll.update_status(payroll_id, data.status, db)
