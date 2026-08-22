from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.employee import Employee


def list_records(employee: Employee, db: Session):
    return db.query(Attendance).filter(Attendance.employee_id == employee.id).order_by(Attendance.work_date.desc()).all()


def clock_in(employee: Employee, db: Session):
    record = db.query(Attendance).filter_by(employee_id=employee.id, work_date=date.today()).first()
    if record and record.check_in:
        raise HTTPException(status_code=409, detail="Already clocked in today")
    if not record:
        record = Attendance(employee_id=employee.id, work_date=date.today())
        db.add(record)
    record.check_in = datetime.utcnow()
    record.status = "present"
    db.commit()
    db.refresh(record)
    return record


def clock_out(employee: Employee, db: Session):
    record = db.query(Attendance).filter_by(employee_id=employee.id, work_date=date.today()).first()
    if not record or not record.check_in:
        raise HTTPException(status_code=400, detail="Clock in before clocking out")
    if record.check_out:
        raise HTTPException(status_code=409, detail="Already clocked out today")
    record.check_out = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record
