from typing import Annotated
from fastapi import APIRouter, Depends
from app.utils.dependencies import DbSession
from app.models.employee import Employee
from app.models.user import User
from app.schemas.leave import LeaveCreate, LeaveResponse, LeaveStatusUpdate
from app.services import leave
from app.utils.dependencies import current_user, require_roles

router = APIRouter()


@router.get("/admin/all", response_model=list[LeaveResponse])
def list_all_leaves(user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    return leave.list_all(db)


@router.get("/", response_model=list[LeaveResponse])
def list_leaves(user: Annotated[User, Depends(current_user)], db: DbSession):
    employee = db.query(Employee).filter_by(user_id=user.id).first()
    return leave.list_requests(employee, db)


@router.post("/", response_model=LeaveResponse)
def request_leave(data: LeaveCreate, user: Annotated[User, Depends(current_user)], db: DbSession):
    employee = db.query(Employee).filter_by(user_id=user.id).first()
    return leave.create_request(employee, data, db)


@router.patch("/{leave_id}/status", response_model=LeaveResponse)
def update_leave_status(leave_id: int, data: LeaveStatusUpdate, user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    return leave.update_status(leave_id, data.status, db)
