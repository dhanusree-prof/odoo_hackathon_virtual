from typing import Annotated
from fastapi import APIRouter, Depends
from app.database.connection import get_db
from app.models.employee import Employee
from app.models.user import User
from app.schemas.attendance import AttendanceResponse
from app.services import attendance
from app.utils.dependencies import DbSession, current_user

router = APIRouter()


def get_employee(user: User, db: DbSession) -> Employee:
    return db.query(Employee).filter_by(user_id=user.id).first()


@router.get("/", response_model=list[AttendanceResponse])
def list_attendance(user: Annotated[User, Depends(current_user)], db: DbSession):
    return attendance.list_records(get_employee(user, db), db)


@router.post("/clock-in", response_model=AttendanceResponse)
def clock_in(user: Annotated[User, Depends(current_user)], db: DbSession):
    return attendance.clock_in(get_employee(user, db), db)


@router.post("/clock-out", response_model=AttendanceResponse)
def clock_out(user: Annotated[User, Depends(current_user)], db: DbSession):
    return attendance.clock_out(get_employee(user, db), db)
