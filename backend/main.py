from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import init_db
from app.routes import attendance, authentication, employee, leave, payroll, reports

app = FastAPI(title="Dayflow HRMS API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(employee.router, prefix="/api/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(leave.router, prefix="/api/leaves", tags=["Leave"])
app.include_router(payroll.router, prefix="/api/payroll", tags=["Payroll"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "dayflow-hrms-backend"}
