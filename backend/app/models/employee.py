from typing import Optional
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    full_name: Mapped[str] = mapped_column(String(150))
    department: Mapped[str] = mapped_column(String(100), default="General")
    job_title: Mapped[str] = mapped_column(String(100), default="Employee")
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    user: Mapped["User"] = relationship(back_populates="employee")
