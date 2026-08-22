from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.schemas.leave import LeaveCreate


def list_requests(employee: Employee, db: Session):
    return db.query(LeaveRequest).filter_by(employee_id=employee.id).order_by(LeaveRequest.created_at.desc()).all()


def create_request(employee: Employee, data: LeaveCreate, db: Session):
    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="end_date must be on or after start_date")
    request = LeaveRequest(employee_id=employee.id, **data.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
