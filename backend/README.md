# Dayflow HRMS Backend

FastAPI backend for the Dayflow HRMS frontend.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

API documentation is available at `http://127.0.0.1:8000/docs`.

The default database is SQLite. Set `DATABASE_URL` in `.env` to use another SQLAlchemy-supported database.
