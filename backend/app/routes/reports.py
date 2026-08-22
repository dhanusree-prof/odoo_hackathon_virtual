from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import func
from app.utils.dependencies import DbSession
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.user import User
from app.utils.dependencies import require_roles

router = APIRouter()


@router.get("/summary")
def summary(user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    return {
        "employees": db.query(func.count(Employee.id)).scalar() or 0,
        "attendance_records": db.query(func.count(Attendance.id)).scalar() or 0,
        "pending_leaves": db.query(func.count(LeaveRequest.id)).filter(LeaveRequest.status == "pending").scalar() or 0,
    }
