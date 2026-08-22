from datetime import datetime
from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(Enum("employee", "admin", "hr", name="user_roles"), default="employee")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    employee: Mapped["Employee"] = relationship(back_populates="user", uselist=False)
