from app.database.connection import Base, engine
from app.models import Attendance, Employee, LeaveRequest, Payroll, User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
