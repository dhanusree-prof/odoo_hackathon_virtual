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
