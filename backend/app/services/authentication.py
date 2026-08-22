from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.user import User
from app.schemas.user import LoginRequest, UserCreate
from app.utils.security import create_access_token, hash_password, verify_password


def register(data: UserCreate, db: Session) -> dict:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.flush()
    db.add(Employee(user_id=user.id, full_name=data.full_name, department=data.department, job_title=data.job_title))
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer", "user": user}


def login(data: LoginRequest, db: Session) -> dict:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer", "user": user}
