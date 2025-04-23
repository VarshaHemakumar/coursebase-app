
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from functools import wraps
import traceback

from utils.recommender import get_recommendations_for


from db_config import get_connection  
import psycopg2

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import io
import base64


import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = 'your_secret_key'


from functools import wraps
from flask import session, flash, redirect, url_for

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from db_config import get_connection  

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'email' not in session:
                flash("Please log in", "warning")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("Unauthorized access", "danger")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@app.route('/')
def root():
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/student/dashboard')
@login_required(role='student')
def student_dashboard():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        student_id = session.get('student_id')

        # Fetch student details
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()

        # Fetch trending courses
        cursor.execute("""
            SELECT c.course_name, ROUND(AVG(r.rating_score), 2) AS avg_rating
            FROM courses c
            JOIN ratings r ON c.course_id = r.course_id
            GROUP BY c.course_id
            ORDER BY avg_rating DESC
            LIMIT 5
        """)
        trending_courses = cursor.fetchall()

        return render_template(
            'student_dashboard.html',
            student=student,
            trending_courses=trending_courses
        )

    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for('login'))
    finally:
        if conn:
            conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, email, role FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]
                session['email'] = user[1]
                session['role'] = user[2]

                # Fetch student_id if user is a student
                if session['role'] == 'student':
                    cursor.execute("SELECT student_id FROM students WHERE email = %s", (email,))
                    student = cursor.fetchone()
                    if student:
                        session['student_id'] = student[0]
                    else:
                        flash("Student not found in student table.", "danger")
                        return redirect(url_for('logout'))

                flash("Login successful!", "success")
                return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'student_dashboard'))

            else:
                flash("Invalid email or password.", "danger")

        except Exception as e:
            flash(f"Login error: {str(e)}", "danger")

        finally:
            if conn:
                conn.close()

    return render_template('login.html')


@app.route('/admin/students')
@login_required(role='admin')
def manage_students():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY student_id DESC")
        students = cursor.fetchall()
        return render_template('admin_students.html', students=students)
    except Exception as e:
        flash(f"Error loading students: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (student_id, name, email, department) 
                VALUES (%s, %s, %s, %s)
            """, (student_id, name, email, department))
            conn.commit()
            flash("Student added successfully.", "success")
            return redirect(url_for('manage_students'))
        except Exception as e:
            flash(f"Failed to add student: {str(e)}", "danger")
        finally:
            if conn:
                conn.close()
    return render_template('student_form.html', action="Add")

@app.route('/admin/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        try:
            cursor.execute("UPDATE students SET name=%s, email=%s, department=%s WHERE student_id=%s",
                           (name, email, department, student_id))
            conn.commit()
            flash("Student updated successfully.", "success")
            return redirect(url_for('manage_students'))
        except Exception as e:
            flash(f"Update failed: {str(e)}", "danger")
    else:
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        return render_template('student_form.html', student=student, action="Edit")


@app.route('/admin/students/delete/<int:student_id>')
@login_required(role='admin')
def delete_student(student_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        flash("Student deleted successfully.", "success")
    except Exception as e:
        error_msg = str(e)
        if "trg_block_protected_students" in error_msg or "prevent_protected_student_delete" in error_msg:
            flash("This student is protected and cannot be deleted.", "warning")
        else:
            flash(f"Error deleting student: {error_msg}", "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage_students'))



@app.route('/admin/attendance', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_view_attendance():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch student options
        cursor.execute("SELECT student_id, name FROM students")
        student_list = cursor.fetchall()

        selected_id = request.form.get('student_id') if request.method == 'POST' else None

        # Fetch attendance data (filtered if selected)
        if selected_id:
            cursor.execute("""
                SELECT s.student_id, s.name, c.course_name, se.session_time, ad.attendance_status
                FROM attendance_details ad
                JOIN session_attendance sa ON ad.session_id = sa.session_id AND ad.student_id = sa.student_id
                JOIN sessions se ON se.session_id = sa.session_id
                JOIN students s ON s.student_id = ad.student_id
                JOIN courses c ON c.course_id = se.course_id
                WHERE s.student_id = %s
                ORDER BY se.session_time DESC
            """, (selected_id,))
        else:
            cursor.execute("""
                SELECT s.student_id, s.name, c.course_name, se.session_time, ad.attendance_status
                FROM attendance_details ad
                JOIN session_attendance sa ON ad.session_id = sa.session_id AND ad.student_id = sa.student_id
                JOIN sessions se ON se.session_id = sa.session_id
                JOIN students s ON s.student_id = ad.student_id
                JOIN courses c ON c.course_id = se.course_id
                ORDER BY se.session_time DESC
            """)

        records = cursor.fetchall()
        return render_template("admin_attendance.html", attendance=records, students=student_list, selected_id=selected_id)

    except Exception as e:
        flash(f"Error loading attendance: {str(e)}", "danger")
        return redirect(url_for("admin_dashboard"))
    finally:
        if conn:
            conn.close()


@app.route('/admin/analytics')
@login_required(role='admin')
def analytics_dashboard():
    return render_template('analytics_dashboard.html')


@app.route('/admin/insights')
@login_required(role='admin')
def insights():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                s.student_id,
                s.name AS student_name,
                s.email,
                s.department,
                c.course_id,
                c.course_name,
                c.credits,
                AVG(r.rating_score) AS average_rating,
                e.semester
            FROM students s
            JOIN student_course sc ON s.student_id = sc.student_id
            JOIN courses c ON sc.course_id = c.course_id
            LEFT JOIN ratings r ON r.course_id = c.course_id AND r.student_id = s.student_id
            LEFT JOIN enrollment_details e ON s.student_id = e.student_id AND c.course_id = e.course_id
            GROUP BY s.student_id, s.name, s.email, s.department, c.course_id, c.course_name, c.credits, e.semester
            ORDER BY s.student_id, c.course_id
        """
        cursor.execute(query)
        insights = cursor.fetchall()

        return render_template('insights.html', insights=insights)

    except Exception as e:
        flash(f"Error loading insights: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn:
            conn.close()



# @app.route('/courses')
# @login_required()
# def view_courses():
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM courses ORDER BY course_id")
#         courses = cursor.fetchall()
#     except Exception as e:
#         flash(f"Error fetching courses: {str(e)}", "danger")
#         courses = []
#     finally:
#         if conn: conn.close()

#     return render_template('courses.html', courses=courses, is_admin=(session.get('role') == 'admin'))

# Enrollments CRUD

@app.route('/admin/enrollments')
@login_required(role='admin')
def admin_view_enrollments():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.student_id, s.name, c.course_id, c.course_name, e.semester
            FROM enrollment_details e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY e.semester DESC
            LIMIT 100
        """)

        enrollments = cursor.fetchall()
        return render_template('admin_enrollments.html', enrollments=enrollments)

    except Exception as e:
        flash(f"Failed to load enrollments: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            conn.close()



@app.route('/admin/enrollments/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_enrollment():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch dropdown data
        cursor.execute("SELECT student_id, name FROM students")
        students = cursor.fetchall()
        cursor.execute("SELECT course_id, course_name FROM courses")
        courses = cursor.fetchall()

        if request.method == 'POST':
            student_id = request.form['student_id']
            course_id = request.form['course_id']
            semester = request.form['semester']

            # Add to student_course if not already present
            cursor.execute("""
                INSERT INTO student_course (student_id, course_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (student_id, course_id))

            # Add to enrollment_details
            cursor.execute("""
                INSERT INTO enrollment_details (student_id, course_id, semester)
                VALUES (%s, %s, %s)
            """, (student_id, course_id, semester))

            conn.commit()
            flash("Enrollment added successfully.", "success")
            return redirect(url_for('admin_view_enrollments'))

        return render_template('add_enrollment.html', students=students, courses=courses)

    except Exception as e:
        flash(f"Error adding enrollment: {str(e)}", "danger")
        return redirect(url_for('admin_view_enrollments'))
    finally:
        if conn: conn.close()


@app.route('/admin/enrollments/delete', methods=['POST'])
@login_required(role='admin')
def delete_enrollment():
    try:
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        semester = request.form['semester']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM enrollment_details
            WHERE student_id = %s AND course_id = %s AND semester = %s
        """, (student_id, course_id, semester))

        conn.commit()
        flash("Enrollment deleted successfully.", "success")

    except Exception as e:
        flash(f"Error deleting enrollment: {str(e)}", "danger")

    finally:
        if conn: conn.close()

    return redirect(url_for('admin_view_enrollments'))



@app.route('/admin/courses')
@login_required(role='admin')
def admin_view_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY course_id DESC")
    courses = cursor.fetchall()
    return render_template('admin_courses.html', courses=courses)


# Courses CRUD


@app.route('/home')
@login_required()
def home():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.course_name, ROUND(AVG(r.rating_score), 2) AS avg_rating
            FROM courses c
            JOIN ratings r ON c.course_id = r.course_id
            GROUP BY c.course_id
            ORDER BY avg_rating DESC
            LIMIT 6
        """)
        trending_courses = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading trending courses: {str(e)}", "danger")
        trending_courses = []
    finally:
        if conn:
            conn.close()

    return render_template("home.html", trending_courses=trending_courses)



# ADMIN: View All Courses
# @app.route('/admin/courses')
# @login_required(role='admin')
# def admin_view_courses():
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM courses ORDER BY course_id ASC")
#         courses = cursor.fetchall()
#         return render_template('courses.html', courses=courses)
#     except Exception as e:
#         flash(f"Failed to fetch courses: {str(e)}", "danger")
#         return redirect(url_for('admin_dashboard'))
#     finally:
#         if conn: conn.close()

# STUDENT: Browse Courses
@app.route('/student/courses')
@login_required(role='student')
def student_view_courses():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY course_id ASC")
        courses = cursor.fetchall()
        return render_template('courses.html', courses=courses)
    except Exception as e:
        flash(f"Failed to fetch courses: {str(e)}", "danger")
        return redirect(url_for('student_dashboard'))
    finally:
        if conn: conn.close()


@app.route('/courses/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_course():
    if request.method == 'POST':
        name = request.form['course_name']
        department = request.form['department']
        credits = int(request.form['credits'])
        difficulty = request.form['difficulty_level']

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Manually compute next course_id
            cursor.execute("SELECT MAX(course_id) FROM courses")
            max_id = cursor.fetchone()[0]
            next_course_id = 1 if max_id is None else max_id + 1

            # Now insert with manually generated course_id
            cursor.execute("""
                INSERT INTO courses (course_id, course_name, department, credits, difficulty_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (next_course_id, name, department, credits, difficulty))

            conn.commit()
            flash("Course added successfully!", "success")
            return redirect(url_for('admin_view_courses'))  # make sure this matches your route name
        except Exception as e:
            flash(f"Failed to add course: {str(e)}", "danger")
        finally:
            if conn:
                conn.close()

    return render_template('course_form.html', action="Add", course=None)


@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_course(course_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            name = request.form['course_name']
            department = request.form['department']
            credits = request.form['credits']
            difficulty = request.form['difficulty_level']

            cursor.execute("""
                UPDATE courses
                SET course_name = %s,
                    department = %s,
                    credits = %s,
                    difficulty_level = %s
                WHERE course_id = %s
            """, (name, department, credits, difficulty, course_id))
            conn.commit()
            flash("Course updated successfully!", "success")
            return redirect(url_for('admin_view_courses'))

        cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
        course = cursor.fetchone()
        return render_template("course_form.html", action="Edit", course=course)
    except Exception as e:
        flash(f"Error editing course: {str(e)}", "danger")
        return redirect(url_for('admin_view_courses'))
    finally:
        if conn: conn.close()


@app.route('/courses/delete/<int:course_id>')
@login_required(role='admin')
def delete_course(course_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
        conn.commit()
        flash("Course deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting course: {str(e)}", "danger")
    finally:
        if conn: conn.close()

    return redirect(url_for('admin_view_courses'))


@app.route('/student/attendance')
@login_required(role='student')
def view_attendance():
    try:
        student_id = session.get('student_id')
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.course_name, s.session_time, ad.attendance_status
            FROM attendance_details ad
            JOIN session_attendance sa ON ad.session_id = sa.session_id AND ad.student_id = sa.student_id
            JOIN sessions s ON sa.session_id = s.session_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE ad.student_id = %s
            ORDER BY s.session_time DESC
        """, (student_id,))
        attendance = cursor.fetchall()

        return render_template('view_attendance.html', attendance=attendance)

    except Exception as e:
        flash(f"Error loading attendance: {str(e)}", "danger")
        return redirect(url_for('student_dashboard'))

    finally:
        if conn:
            conn.close()


@app.route('/student/recommendations')
@login_required(role='student')
def student_recommendations():
    try:
        student_id = session.get('student_id')
        recommendations = get_recommendations_for(student_id)

        return render_template('recommendations.html', recommendations=recommendations)

    except Exception as e:
        flash(f"Recommendation error: {str(e)}", "danger")
        return redirect(url_for('student_dashboard'))


@app.route('/student/enrollments')
@login_required(role='student')
def student_enrollments():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.student_id, c.course_id, c.course_name, e.semester
            FROM enrollment_details e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = %s
            ORDER BY e.semester DESC
        """, (session['student_id'],))
        
        enrollments = cursor.fetchall()
        print("DEBUG: Enrollments fetched:", enrollments)  # 🧪 Debug line

        if not enrollments:
            flash("No enrollments found for your account.", "info")

        return render_template('student_enrollments.html', enrollments=enrollments)
    
    except Exception as e:
        flash(f"Error loading enrolled courses: {str(e)}", "danger")
        return redirect(url_for('student_dashboard'))
    
    finally:
        if conn:
            conn.close()



@app.route('/student/courses')
@login_required(role='student')
def view_courses():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        conn.close()
        return render_template('view_courses.html', courses=courses)
    except Exception as e:
        flash(f"Error loading courses: {str(e)}", "danger")
        return redirect(url_for('student_dashboard'))

@app.route('/admin/courses')
@login_required(role='admin')
def admin_manage_courses():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY course_id")
        courses = cursor.fetchall()
        return render_template('admin_courses.html', courses=courses)
    except Exception as e:
        flash(f"Error loading courses: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn: conn.close()


@app.route('/student/profile')
@login_required(role='student')
def student_profile():
    try:
        student_id = session.get('student_id')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        conn.close()
        return render_template('student_profile.html', student=student)
    except Exception as e:
        flash(f"Error loading profile: {str(e)}", "danger")
        return redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))



@app.route('/recommendations', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_recommend_input(): 
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get all students for dropdown
        cursor.execute("SELECT student_id, name FROM students")
        students = cursor.fetchall()

        selected_id = None
        enrolled = []
        recommendations = []

        if request.method == 'POST':
            selected_id = int(request.form.get('student_id'))

        if selected_id:
            # Get enrolled course names
            cursor.execute("""
                SELECT c.course_name
                FROM enrollment_details ed
                JOIN courses c ON ed.course_id = c.course_id
                WHERE ed.student_id = %s
            """, (selected_id,))
            enrolled = [row[0] for row in cursor.fetchall()]

            # Get recommendations
            from utils.recommender import get_recommendations_for
            recommendations = get_recommendations_for(selected_id)

        return render_template(
            'recommend_input.html',
            students=students,
            student_id=selected_id,
            enrolled=enrolled,
            recommendations=recommendations
        )

    except Exception as e:
        flash(f"Recommendation error: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))

    finally:
        if conn: conn.close()


if __name__ == '__main__':
    app.run(debug=True)
