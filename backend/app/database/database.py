from app.database.connection import Base, engine
from app.models import Attendance, Employee, LeaveRequest, Payroll, User
from app.utils.security import hash_password
from app.database.connection import settings


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.database_url.startswith("sqlite"):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            admin_email = "admin@dayflow.com"
            if not db.query(User).filter_by(email=admin_email).first():
                user = User(email=admin_email, password_hash=hash_password("Admin123!"), role="admin")
                db.add(user)
                db.flush()
                db.add(Employee(user_id=user.id, full_name="Dayflow Administrator", department="People Operations", job_title="HR Administrator"))
                db.commit()
        finally:
            db.close()
