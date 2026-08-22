from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.utils.dependencies import DbSession
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import EmployeeResponse
from app.utils.dependencies import current_user, require_roles

router = APIRouter()


@router.get("/me", response_model=EmployeeResponse)
def profile(user: Annotated[User, Depends(current_user)], db: DbSession):
    employee = db.query(Employee).filter_by(user_id=user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(user: Annotated[User, Depends(require_roles("admin", "hr"))], db: DbSession):
    return db.query(Employee).all()
