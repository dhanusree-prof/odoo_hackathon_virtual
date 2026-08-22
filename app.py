from datetime import date, datetime
from functools import wraps
from pathlib import Path
import sqlite3

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "dayflow-demo-key"
app.config["DATABASE"] = Path(app.root_path) / "dayflow.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('employee', 'admin')));
CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL REFERENCES users(id), name TEXT NOT NULL, job_title TEXT NOT NULL, department TEXT NOT NULL, phone TEXT NOT NULL, location TEXT NOT NULL, joined TEXT NOT NULL, salary REAL NOT NULL DEFAULT 0, leave_allowance INTEGER NOT NULL DEFAULT 22);
CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id INTEGER NOT NULL REFERENCES employees(id), work_date TEXT NOT NULL, check_in TEXT, check_out TEXT, status TEXT NOT NULL DEFAULT 'Present');
CREATE TABLE IF NOT EXISTS leave_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id INTEGER NOT NULL REFERENCES employees(id), leave_type TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, note TEXT, status TEXT NOT NULL DEFAULT 'Pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS payroll (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id INTEGER NOT NULL REFERENCES employees(id), pay_period TEXT NOT NULL, payment_date TEXT NOT NULL, gross_pay REAL NOT NULL, net_pay REAL NOT NULL, status TEXT NOT NULL DEFAULT 'Pending');
CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, detail TEXT NOT NULL, kind TEXT NOT NULL, created_at TEXT NOT NULL);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def seed_database():
    db = get_db()
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return
    db.execute("INSERT INTO users(email,password_hash,role) VALUES(?,?,?)", ("olivia@dayflow.io", generate_password_hash("password"), "employee"))
    employee_user = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO users(email,password_hash,role) VALUES(?,?,?)", ("admin@dayflow.io", generate_password_hash("password"), "admin"))
    db.execute("INSERT INTO employees(user_id,name,job_title,department,phone,location,joined,salary) VALUES(?,?,?,?,?,?,?,?)", (employee_user, "Olivia Rhye", "Product Designer", "Design & Experience", "+1 (555) 014-2876", "New York, NY", "March 18, 2022", 101400))
    employee_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO attendance(employee_id,work_date,check_in,status) VALUES(?,?,?,?)", (employee_id, date.today().isoformat(), "08:42", "Present"))
    db.executemany("INSERT INTO payroll(employee_id,pay_period,payment_date,gross_pay,net_pay,status) VALUES(?,?,?,?,?,?)", [(employee_id, "September 2024", "2024-09-30", 8450, 6284.17, "Paid"), (employee_id, "August 2024", "2024-08-30", 8450, 6284.17, "Paid"), (employee_id, "July 2024", "2024-07-31", 8450, 6284.17, "Paid")])
    db.executemany("INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,note,status,created_at) VALUES(?,?,?,?,?,?,?)", [(employee_id, "Annual leave", "2024-11-04", "2024-11-08", "", "Approved", datetime.utcnow().isoformat()), (employee_id, "Personal day", "2024-12-20", "2024-12-20", "", "Pending", datetime.utcnow().isoformat())])
    db.executemany("INSERT INTO announcements(title,detail,kind,created_at) VALUES(?,?,?,?)", [("Open enrollment is here", "Review your benefit elections before Friday, Oct 25.", "spark", datetime.utcnow().isoformat()), ("Design team offsite", "A quick reminder about next Thursday's team gathering.", "calendar", datetime.utcnow().isoformat())])
    db.commit()

EMPLOYEE = {
    "name": "Olivia Rhye",
    "initials": "OR",
    "role": "Product Designer",
    "department": "Design & Experience",
    "email": "olivia@dayflow.io",
    "phone": "+1 (555) 014-2876",
    "location": "New York, NY",
    "joined": "March 18, 2022",
}

ANNOUNCEMENTS = [
    {"title": "Open enrollment is here", "detail": "Review your benefit elections before Friday, Oct 25.", "time": "2 hours ago", "type": "spark"},
    {"title": "Design team offsite", "detail": "A quick reminder about next Thursday's team gathering.", "time": "Yesterday", "type": "calendar"},
]

LEAVE_REQUESTS = [
    {"kind": "Annual leave", "dates": "Nov 04 - Nov 08, 2024", "days": "5 days", "status": "Approved", "tone": "approved"},
    {"kind": "Personal day", "dates": "Dec 20, 2024", "days": "1 day", "status": "Pending", "tone": "pending"},
]

PAYSLIPS = [
    {"month": "September 2024", "date": "Sep 30, 2024", "gross": "$8,450.00", "net": "$6,284.17", "status": "Paid"},
    {"month": "August 2024", "date": "Aug 30, 2024", "gross": "$8,450.00", "net": "$6,284.17", "status": "Paid"},
    {"month": "July 2024", "date": "Jul 31, 2024", "gross": "$8,450.00", "net": "$6,284.17", "status": "Paid"},
]


with app.app_context():
    seed_database()


def current_employee():
    if not session.get("user_id"):
        return None
    return get_db().execute("SELECT e.*, e.job_title AS role, substr(e.name, 1, 1) || substr(e.name, instr(e.name, ' ') + 1, 1) AS initials, u.email FROM employees e JOIN users u ON u.id=e.user_id WHERE e.user_id=?", (session["user_id"],)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return login_required(wrapped)


@app.context_processor
def inject_globals():
    employee = current_employee()
    if employee is None and session.get("role") == "admin":
        employee = {"name": "Dayflow Admin", "role": "Administrator", "initials": "DA", "email": "admin@dayflow.io"}
    return {"employee": employee, "current_year": date.today().year, "is_admin": session.get("role") == "admin"}


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user or not check_password_hash(user["password_hash"], request.form.get("password", "")):
            flash("Incorrect email or password.", "error")
            return render_template("login.html"), 401
        session.clear()
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            flash("That email is already registered.", "error")
            return render_template("register.html"), 409
        db.execute("INSERT INTO users(email,password_hash,role) VALUES(?,?,?)", (email, generate_password_hash(request.form["password"]), "employee"))
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.execute("INSERT INTO employees(user_id,name,job_title,department,phone,location,joined,salary) VALUES(?,?,?,?,?,?,?,?)", (user_id, request.form["name"], request.form.get("job_title", "Team member"), request.form.get("department", "General"), request.form.get("phone", ""), request.form.get("location", ""), date.today().strftime("%B %d, %Y"), 0))
        db.commit()
        flash("Account created. You can now sign in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("role") == "admin":
        db = get_db()
        employees = db.execute("SELECT e.*, u.email FROM employees e JOIN users u ON u.id=e.user_id ORDER BY e.name").fetchall()
        attendance_rows = db.execute("SELECT a.*, e.name FROM attendance a JOIN employees e ON e.id=a.employee_id ORDER BY a.work_date DESC, e.name").fetchall()
        payroll_rows = db.execute("SELECT p.*, e.name FROM payroll p JOIN employees e ON e.id=p.employee_id ORDER BY p.payment_date DESC").fetchall()
        leave_rows = db.execute("SELECT l.*, e.name FROM leave_requests l JOIN employees e ON e.id=l.employee_id ORDER BY l.created_at DESC").fetchall()
        pending_leave = sum(row["status"] == "Pending" for row in leave_rows)
        return render_template("admin_controls.html", active_page="dashboard", employees=employees, attendance_rows=attendance_rows, payroll_rows=payroll_rows, leave_rows=leave_rows, pending_leave=pending_leave)
    announcements = get_db().execute("SELECT id,title,detail,kind AS type,created_at FROM announcements ORDER BY created_at DESC").fetchall()
    return render_template("employee_dashboard_live.html", active_page="dashboard", announcements=announcements)


@app.route("/admin/employee/<int:employee_id>/update", methods=["POST"])
@admin_required
def update_employee(employee_id):
    db = get_db()
    db.execute("UPDATE employees SET name=?, job_title=?, department=?, salary=? WHERE id=?", (request.form["name"], request.form["job_title"], request.form["department"], float(request.form["salary"]), employee_id))
    db.commit()
    flash("Employee and salary details saved.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/attendance/<int:attendance_id>/update", methods=["POST"])
@admin_required
def update_attendance(attendance_id):
    db = get_db()
    db.execute("UPDATE attendance SET work_date=?, check_in=?, check_out=?, status=? WHERE id=?", (request.form["work_date"], request.form["check_in"], request.form["check_out"], request.form["status"], attendance_id))
    db.commit()
    flash("Attendance timing saved.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/payroll/<int:payroll_id>/update", methods=["POST"])
@admin_required
def update_payroll(payroll_id):
    db = get_db()
    db.execute("UPDATE payroll SET pay_period=?, payment_date=?, gross_pay=?, net_pay=?, status=? WHERE id=?", (request.form["pay_period"], request.form["payment_date"], float(request.form["gross_pay"]), float(request.form["net_pay"]), request.form["status"], payroll_id))
    db.commit()
    flash("Payroll record saved.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/leave/<int:request_id>/<status>")
@admin_required
def update_leave(request_id, status):
    if status not in {"Approved", "Rejected", "Pending"}:
        abort(400)
    db = get_db()
    db.execute("UPDATE leave_requests SET status=? WHERE id=?", (status, request_id))
    db.commit()
    flash(f"Leave request {status.lower()}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    employee = current_employee()
    if request.method == "POST":
        db = get_db()
        db.execute("UPDATE employees SET name=?, phone=?, location=? WHERE id=?", (request.form["name"], request.form["phone"], request.form["location"], employee["id"]))
        db.commit()
        flash("Profile saved.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", active_page="profile")


@app.route("/attendance")
@login_required
def attendance():
    employee = current_employee()
    rows = get_db().execute("SELECT * FROM attendance WHERE employee_id=? ORDER BY work_date DESC", (employee["id"],)).fetchall()
    return render_template("attendance.html", active_page="attendance", attendance_rows=rows)


@app.route("/leave", methods=["GET", "POST"])
@login_required
def leave():
    employee = current_employee()
    if request.method == "POST":
        db = get_db()
        db.execute("INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,note,created_at) VALUES(?,?,?,?,?,?)", (employee["id"], request.form["leave_type"], request.form["start_date"], request.form["end_date"], request.form.get("note", ""), datetime.utcnow().isoformat()))
        db.commit()
        flash("Leave request submitted.", "success")
        return redirect(url_for("leave"))
    leave_requests = get_db().execute("SELECT *, leave_type AS kind, start_date || ' - ' || end_date AS dates, CAST(julianday(end_date) - julianday(start_date) + 1 AS INTEGER) || ' days' AS days, CASE WHEN status='Approved' THEN 'approved' WHEN status='Rejected' THEN 'late' ELSE 'pending' END AS tone FROM leave_requests WHERE employee_id=? ORDER BY created_at DESC", (employee["id"],)).fetchall()
    return render_template("leave.html", active_page="leave", leave_requests=leave_requests)


@app.route("/payroll")
@login_required
def payroll():
    employee = current_employee()
    payslips = get_db().execute("SELECT *, pay_period AS month, payment_date AS date, printf('$%,.2f', gross_pay) AS gross, printf('$%,.2f', net_pay) AS net FROM payroll WHERE employee_id=? ORDER BY payment_date DESC", (employee["id"],)).fetchall()
    return render_template("payroll.html", active_page="payroll", payslips=payslips)


if __name__ == "__main__":
    app.run(debug=True)
