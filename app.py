"""
Student Record Management System
A beginner-friendly Flask application using SQLite (sqlite3 only, no ORM).
"""

import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = "student_record_secret_key"  # needed for flash messages

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


# ---------------------------------------------------------------------------
# Database helper functions
# ---------------------------------------------------------------------------
def get_db():
    """Open a new database connection if one doesn't already exist for this request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # allows accessing columns by name
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the students table if it doesn't exist, and insert sample data if empty."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()

    # Insert sample records only if table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_students = [
            ("STU001", "Alice Johnson", "Computer Science", "2nd Year", "alice.johnson@example.com", "9876543210"),
            ("STU002", "Bob Smith", "Mechanical Engineering", "3rd Year", "bob.smith@example.com", "9876543211"),
            ("STU003", "Charlie Brown", "Electrical Engineering", "1st Year", "charlie.brown@example.com", "9876543212"),
            ("STU004", "Diana Prince", "Civil Engineering", "4th Year", "diana.prince@example.com", "9876543213"),
            ("STU005", "Ethan Hunt", "Computer Science", "3rd Year", "ethan.hunt@example.com", "9876543214"),
        ]
        cursor.executemany("""
            INSERT INTO students (student_id, full_name, department, year, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_students)
        conn.commit()

    conn.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Home dashboard - shows summary statistics."""
    db = get_db()
    total_students = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    departments = db.execute("SELECT COUNT(DISTINCT department) FROM students").fetchone()[0]
    recent_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT 5"
    ).fetchall()
    return render_template(
        "index.html",
        total_students=total_students,
        departments=departments,
        recent_students=recent_students,
    )


@app.route("/students")
def students():
    """View all students, with optional search by ID or name."""
    db = get_db()
    query = request.args.get("query", "").strip()

    if query:
        search_term = f"%{query}%"
        all_students = db.execute(
            """
            SELECT * FROM students
            WHERE student_id LIKE ? OR full_name LIKE ?
            ORDER BY id ASC
            """,
            (search_term, search_term),
        ).fetchall()
        if not all_students:
            flash(f"No students found matching '{query}'.", "error")
    else:
        all_students = db.execute("SELECT * FROM students ORDER BY id ASC").fetchall()

    return render_template("students.html", students=all_students, query=query)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    """Add a new student record."""
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        full_name = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        # --- Basic form validation ---
        if not (student_id and full_name and department and year and email and phone):
            flash("All fields are required.", "error")
            return render_template("add_student.html", form_data=request.form)

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("add_student.html", form_data=request.form)

        if not phone.isdigit() or len(phone) < 7:
            flash("Please enter a valid phone number (digits only).", "error")
            return render_template("add_student.html", form_data=request.form)

        db = get_db()
        try:
            db.execute(
                """
                INSERT INTO students (student_id, full_name, department, year, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (student_id, full_name, department, year, email, phone),
            )
            db.commit()
            flash(f"Student '{full_name}' added successfully!", "success")
            return redirect(url_for("students"))
        except sqlite3.IntegrityError:
            flash(f"Student ID '{student_id}' already exists. Please use a unique ID.", "error")
            return render_template("add_student.html", form_data=request.form)
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "error")
            return render_template("add_student.html", form_data=request.form)

    return render_template("add_student.html", form_data={})


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    """Edit an existing student record."""
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        full_name = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        # --- Basic form validation ---
        if not (student_id and full_name and department and year and email and phone):
            flash("All fields are required.", "error")
            return render_template("edit_student.html", student=request.form, id=id)

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("edit_student.html", student=request.form, id=id)

        if not phone.isdigit() or len(phone) < 7:
            flash("Please enter a valid phone number (digits only).", "error")
            return render_template("edit_student.html", student=request.form, id=id)

        try:
            db.execute(
                """
                UPDATE students
                SET student_id = ?, full_name = ?, department = ?, year = ?, email = ?, phone = ?
                WHERE id = ?
                """,
                (student_id, full_name, department, year, email, phone, id),
            )
            db.commit()
            flash(f"Student '{full_name}' updated successfully!", "success")
            return redirect(url_for("students"))
        except sqlite3.IntegrityError:
            flash(f"Student ID '{student_id}' already exists. Please use a unique ID.", "error")
            return render_template("edit_student.html", student=request.form, id=id)
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "error")
            return render_template("edit_student.html", student=request.form, id=id)

    return render_template("edit_student.html", student=student, id=id)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    """Delete a student record."""
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()

    if student is None:
        flash("Student not found.", "error")
    else:
        db.execute("DELETE FROM students WHERE id = ?", (id,))
        db.commit()
        flash(f"Student '{student['full_name']}' deleted successfully!", "success")

    return redirect(url_for("students"))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", content="Page not found."), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("base.html", content="Internal server error."), 500


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()  # ensure database and table exist before running
    app.run(debug=True)
