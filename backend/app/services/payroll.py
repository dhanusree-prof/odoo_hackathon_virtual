from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.payroll import Payroll
from app.schemas.payroll import PayrollCreate


def list_records(employee: Employee, db: Session):
    return db.query(Payroll).filter_by(employee_id=employee.id).order_by(Payroll.period.desc()).all()


def create_record(employee: Employee, data: PayrollCreate, db: Session):
    record = Payroll(employee_id=employee.id, **data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_all(db: Session):
    return db.query(Payroll).order_by(Payroll.period.desc()).all()


def update_status(record_id: int, status: str, db: Session):
    if status not in {"pending", "paid", "cancelled"}:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="status must be pending, paid, or cancelled")
    record = db.get(Payroll, record_id)
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Payroll record not found")
    record.status = status
    db.commit()
    db.refresh(record)
    return record
