from flask import Flask, render_template,request, redirect, url_for,session
from database import create_tables, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
#secret key for login sessions
app.secret_key = "college-placement-secret-key"


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- STUDENT REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]
        skills = request.form["skills"]
        password = request.form["password"]

        # Convert password into a secure hash
        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO students
                (name, email, phone, department, year, cgpa, skills, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                department,
                year,
                cgpa,
                skills,
                hashed_password
            ))

            connection.commit()

        except Exception as error:
            connection.close()
            return f"Registration failed: {error}"
        connection.close()
        return redirect(url_for("login"))
    return render_template("register.html")

# ---------------- STUDENT LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        student = connection.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if student and check_password_hash(student["password"], password):

            session["student_id"] = student["id"]
            session["student_name"] = student["name"]

            return redirect(url_for("student_dashboard"))
        
        return render_template(
            "login.html",
            error="Invalid email or password."
        )
    return render_template("login.html") 
    
# ---------------- STUDENT DASHBOARD ----------------

@app.route("/student-dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "student_dashboard.html",
        student_name=session["student_name"]
    )
# ---------------- STUDENT PROFILE ----------------

@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, name, email, phone, department, year, cgpa
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    connection.close()

    if student is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        student=student
    )
        

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))
# ---------------- ABOUT ----------------
@app.route("/about")
def about():
    return render_template("about.html")

#-------------------------admin - login------------------------------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()

        admin = connection.execute(
            "SELECT * FROM admins WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        connection.close()

        if admin:
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]

            return redirect(url_for("admin_dashboard"))

        error = "Invalid admin username or password."

    return render_template(
        "admin_login.html",
        error=error
    )
# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    return render_template(
        "admin_dashboard.html"
    )
# ---------------- MANAGE STUDENTS ----------------
@app.route("/students")
def students():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()

    if search:

        students = connection.execute(
            """
            SELECT id, name, email, phone, department, year, cgpa
            FROM students
            WHERE name LIKE ?
               OR email LIKE ?
               OR department LIKE ?
            ORDER BY id DESC
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:

        students = connection.execute(
            """
            SELECT id, name, email, phone, department, year, cgpa
            FROM students
            ORDER BY id DESC
            """
        ).fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students,
        search=search
    )

    
# ---------------- ADD STUDENT ----------------

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    error = None

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO students
                (name, email, phone, department, year, cgpa, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    phone,
                    department,
                    year,
                    cgpa,
                    hashed_password
                )
            )

            connection.commit()

        except Exception as e:

            connection.close()

            error = "Email already exists or invalid student information."

            return render_template(
                "add_student.html",
                error=error
            )

        connection.close()

        return redirect(url_for("students"))

    return render_template("add_student.html")
# ---------------- EDIT STUDENT ----------------

@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if not student:
        connection.close()
        return "Student not found"

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]

        try:

            connection.execute(
                """
                UPDATE students
                SET name = ?,
                    email = ?,
                    phone = ?,
                    department = ?,
                    year = ?,
                    cgpa = ?
                WHERE id = ?
                """,
                (
                    name,
                    email,
                    phone,
                    department,
                    year,
                    cgpa,
                    student_id
                )
            )

            connection.commit()

        except Exception:

            connection.close()

            return render_template(
                "edit_student.html",
                student=student,
                error="Email already exists."
            )

        connection.close()

        return redirect(url_for("students"))

    connection.close()

    return render_template(
        "edit_student.html",
        student=student
    )
# ---------------- DELETE STUDENT ----------------

@app.route("/delete-student/<int:student_id>")
def delete_student(student_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()
    
    return redirect(url_for("students"))

# ---------------- VIEW COMPANIES ----------------

@app.route("/companies")
def companies():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    companies = connection.execute(
        """
        SELECT *
        FROM companies
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "companies.html",
        companies=companies
    )

# ---------------- ADD COMPANY ----------------

@app.route("/add-company", methods=["GET", "POST"])
def add_company():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    error = None

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        location = request.form["location"]
        website = request.form["website"]

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO companies
                (name, email, phone, location, website)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    phone,
                    location,
                    website
                )
            )

            connection.commit()

        except Exception as e:

            connection.close()

            error = "Unable to add company."

            return render_template(
                "add_company.html",
                error=error
            )

        connection.close()

        return redirect(url_for("companies"))

    return render_template("add_company.html")

# ---------------- EDIT COMPANY ----------------

@app.route("/edit-company/<int:company_id>", methods=["GET", "POST"])
def edit_company(company_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    company = connection.execute(
        "SELECT * FROM companies WHERE id = ?",
        (company_id,)
    ).fetchone()

    if not company:
        connection.close()
        return "Company not found"

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        location = request.form["location"]
        website = request.form["website"]

        connection.execute(
            """
            UPDATE companies
            SET name = ?,
                email = ?,
                phone = ?,
                location = ?,
                website = ?
            WHERE id = ?
            """,
            (
                name,
                email,
                phone,
                location,
                website,
                company_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("companies"))

    connection.close()

    return render_template(
        "edit_company.html",
        company=company
    )
@app.route("/delete-company/<int:company_id>")
def delete_company(company_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM companies WHERE id = ?",
        (company_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("companies"))

@app.route("/add-job", methods=["GET", "POST"])
def add_job():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    companies = connection.execute(
        "SELECT * FROM companies ORDER BY name"
    ).fetchall()

    if request.method == "POST":

        company_id = request.form["company_id"]
        job_title = request.form["job_title"]
        description = request.form["description"]
        required_cgpa = request.form["required_cgpa"]
        required_skills = request.form["required_skills"]
        required_department = request.form["required_department"]
        required_year = request.form["required_year"]
        salary = request.form["salary"]
        deadline = request.form["deadline"]


        connection.execute(
            """
            INSERT INTO jobs
            (
                company_id,
                job_title,
                description,
                required_cgpa,
                required_skills,
                required_department,
                required_year,
                salary,
                deadline
                
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_id,
                job_title,
                description,
                required_cgpa,
                required_skills,
                required_department,
                required_year,
                salary,
                deadline,
                
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin_dashboard"))

    connection.close()

    return render_template(
        "add_job.html",
        companies=companies
    )
@app.route("/jobs")
def jobs():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    jobs = connection.execute(
        """
        SELECT
            jobs.id,
            jobs.job_title,
            jobs.description,
            jobs.required_cgpa,
            jobs.required_skills,
            jobs.salary,
            jobs.deadline,
            companies.name AS company_name
        FROM jobs
        JOIN companies
        ON jobs.company_id = companies.id
        ORDER BY jobs.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs
    )
@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    if not job:
        connection.close()
        return "Job not found"

    companies = connection.execute(
        "SELECT * FROM companies ORDER BY name"
    ).fetchall()

    if request.method == "POST":

        company_id = request.form["company_id"]
        job_title = request.form["job_title"]
        description = request.form["description"]
        required_cgpa = request.form["required_cgpa"]
        required_skills = request.form["required_skills"]
        salary = request.form["salary"]
        deadline = request.form["deadline"]

        connection.execute(
            """
            UPDATE jobs
            SET
                company_id = ?,
                job_title = ?,
                description = ?,
                required_cgpa = ?,
                required_skills = ?,
                salary = ?,
                deadline = ?
            WHERE id = ?
            """,
            (
                company_id,
                job_title,
                description,
                required_cgpa,
                required_skills,
                salary,
                deadline,
                job_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("jobs"))

    connection.close()

    return render_template(
        "edit_job.html",
        job=job,
        companies=companies
    )
@app.route("/delete-job/<int:job_id>", methods=["POST"])
def delete_job(job_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    # Delete applications related to this job first
    connection.execute(
        """
        DELETE FROM applications
        WHERE job_id = ?
        """,
        (job_id,)
    )

    # Delete the job
    connection.execute(
        """
        DELETE FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("jobs"))
@app.route("/student-jobs")
def student_jobs():

    if "student_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    jobs = connection.execute(
        """
        SELECT
            jobs.id,
            jobs.job_title,
            jobs.description,
            jobs.required_cgpa,
            jobs.required_skills,
            jobs.salary,
            jobs.deadline,
            companies.name AS company_name
        FROM jobs
        JOIN companies
        ON jobs.company_id = companies.id
        ORDER BY jobs.id DESC
        """
    ).fetchall()

    connection.close()
    today = date.today().isoformat()

    return render_template(
        "student_jobs.html",
        jobs=jobs,
        today=today
    )

 
# ---------------- ELIGIBILITY CHECK ----------------

@app.route("/check-eligibility/<int:job_id>")
def check_eligibility(job_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    job = connection.execute(
        """
        SELECT jobs.*, companies.name AS company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.id
        WHERE jobs.id = ?
        """,
        (job_id,)
    ).fetchone()

    connection.close()

    if not student:
        return "Student not found", 404

    if not job:
        return "Job not found", 404

    # 1. CGPA CHECK
    eligible = True
    reasons = []

    if student["cgpa"] < job["required_cgpa"]:
        eligible = False
        reasons.append({
            "type": "CGPA",
            "message": "Your CGPA is below the required CGPA.",
            "required": job["required_cgpa"],
            "student": student["cgpa"]
        })

    # 2. DEPARTMENT CHECK
    if (
        job["required_department"]
        and student["department"].strip().upper()
        != job["required_department"].strip().upper()
    ):
        eligible = False
        reasons.append({
            "type": "Department",
            "message": "Your department does not match the job requirement.",
            "required": job["required_department"],
            "student": student["department"]
        })

    # 3. YEAR CHECK
    if (
        job["required_year"]
        and student["year"].strip()
        != job["required_year"].strip()
    ):
        eligible = False
        reasons.append({
            "type": "Year",
            "message": "Your current year does not match the job requirement.",
            "required": job["required_year"],
            "student": student["year"]
        })

    # 4. SKILLS CHECK
    student_skills = [
        skill.strip().lower()
        for skill in (student["skills"] or "").split(",")
        if skill.strip()
    ]

    required_skills = [
        skill.strip().lower()
        for skill in (job["required_skills"] or "").split(",")
        if skill.strip()
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in student_skills
    ]

    if missing_skills:
        eligible = False
        reasons.append({
            "type": "Skills",
            "message": "You are missing some required skills.",
            "required": ", ".join(required_skills),
            "student": ", ".join(student_skills),
            "missing": ", ".join(missing_skills)
        })

    return render_template(
        "eligibility.html",
        student=student,
        job=job,
        eligible=eligible,
        reasons=reasons,
        missing_skills=missing_skills
    )   

    
   
     

@app.route("/public-jobs")
def public_jobs():

    connection = get_db_connection()

    jobs = connection.execute(
        """
        SELECT
            jobs.id,
            jobs.job_title,
            jobs.description,
            jobs.required_cgpa,
            jobs.required_skills,
            jobs.salary,
            jobs.deadline,           
         companies.name AS company_name
        FROM jobs
        JOIN companies
        ON jobs.company_id = companies.id
        ORDER BY jobs.id DESC
        """
    ).fetchall()

    connection.close()

    today = date.today().isoformat()

    return render_template(
        "public_jobs.html",
        jobs=jobs,
        today=today
    )


@app.route("/apply-job/<int:job_id>")
def apply_job(job_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()

    # Check whether the job exists
    job = connection.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    ).fetchone()

    if not job:
        connection.close()
        return "Job not found"
    #check weather the job deadline has passed
    today=date.today().isoformat()

    if job["deadline"] < today:
        connection.close()
        return "this job application deadline is closed."

    # Check whether the student already applied
    existing_application = connection.execute(
        """
        SELECT * FROM applications
        WHERE student_id = ? AND job_id = ?
        """,
        (student_id, job_id)
    ).fetchone()

    if existing_application:
        connection.close()
        return "You have already applied for this job."

    # Add application
    connection.execute(
        """
        INSERT INTO applications
        (student_id, job_id, application_date, status)
        VALUES (?, ?, DATE('now'), 'Applied')
        """,
        (student_id, job_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("student_jobs"))

@app.route("/applications")
def applications():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    applications = connection.execute(
        """
        SELECT
            applications.id,
            students.name AS student_name,
            companies.name AS company_name,
            jobs.job_title,
            applications.application_date,
            applications.status,
            applications.rejection_reason,
            applications.admin_feedback
        FROM applications
        JOIN students
            ON applications.student_id = students.id
        JOIN jobs
            ON applications.job_id = jobs.id
        JOIN companies
            ON jobs.company_id = companies.id
        ORDER BY applications.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "applications.html",
        applications=applications
    )
@app.route("/update-application-status/<int:application_id>", methods=["POST"])
def update_application_status(application_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    status = request.form.get("status","").strip()

    allowed_statuses = [
        "Applied",
        "Shortlisted",
        "Selected",
        "Rejected"
    ]
    if status not in allowed_statuses:
        return "Invalid application status", 400

    rejection_reason = request.form.get(
        "rejection_reason", ""
    ).strip()
    admin_feedback = request.form.get(
        "admin_feedback", ""
    ).strip()

    if status == "Rejected":
        if not rejection_reason or not admin_feedback:
            return (
                "For a rejected application, please provide "
                "a rejection reason and feedback. Go back and try again.",
                400
            )
    else:
        # Clear rejection details if the application is moved
        # to a status other than Rejected
        rejection_reason = None
        admin_feedback = None
    connection = get_db_connection()
    application = connection.execute(
        "SELECT id FROM applications WHERE id = ?",
        (application_id,)
    ).fetchone()

    if not application:
        connection.close()
        return "Application not found", 404

    connection.execute(
        """
        UPDATE applications
        SET status = ?,
            rejection_reason = ?,
            admin_feedback = ?
        WHERE id = ?
        """,
        (
            status,
            rejection_reason,
            admin_feedback,
            application_id
        )
    )

    connection.commit()
    connection.close()

    return redirect(url_for("applications"))

@app.route("/my-applications")
def my_applications():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()

    applications = connection.execute(
        """
        SELECT
            applications.id,
            companies.name AS company_name,
            jobs.job_title,
            applications.application_date,
            applications.status,
            applications.rejection_reason,
            applications.admin_feedback
        FROM applications
        JOIN jobs
            ON applications.job_id = jobs.id
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE applications.student_id = ?
        ORDER BY applications.id DESC
        """,
        (student_id,)
    ).fetchall()

    connection.close()
    # Learning and practice recommendations for rejected applications
    resource_map = {
        "Technical Skills": [
            {
                "title": "GeeksforGeeks — DSA Practice",
                "description": "Practise coding problems and strengthen data structures and algorithms.",
                "url": "https://www.geeksforgeeks.org/practice-problems/gfg-160/"
            },
            {
                "title": "W3Schools — Programming Tutorials",
                "description": "Revise programming fundamentals and learn languages such as Python, Java and SQL.",
                "url": "https://www.w3schools.com/"
            }
        ],
        "Aptitude": [
            {
                "title": "IndiaBIX — Aptitude",
                "description": "Practise quantitative aptitude questions for placement tests.",
                "url": "https://www.indiabix.com/aptitude/"
            },
            {
                "title": "IndiaBIX — Online Aptitude Tests",
                "description": "Test your aptitude skills with online practice questions.",
                "url": "https://www.indiabix.com/online-test/aptitude-test/"
            }
        ],
        "Communication": [
            {
                "title": "British Council — Learn English",
                "description": "Practise English skills to improve your communication.",
                "url": "https://learnenglish.britishcouncil.org/"
            },
        ],
         "Interview Performance": [
            {
                "title": "GeeksforGeeks — Interview Experiences",
                "description": "Explore interview experiences and prepare for technical interviews.",
                "url": "https://www.geeksforgeeks.org/"
            }
        ],
        "Resume": [
            {
                "title": "Harvard — Resume and Cover Letter Guide",
                "description": "Review guidance for preparing a clear, professional resume.",
                "url": "https://careerservices.fas.harvard.edu/resources/create-a-resume-cv-or-cover-letter/"
            }
        ],
        "Other": [
            {
                "title": "GeeksforGeeks — Placement Preparation",
                "description": "Explore programming, interview preparation and placement practice.",
                "url": "https://www.geeksforgeeks.org/"
            }
        ]
    }

    # Attach resources to each rejected application
    application_feedback = []

    for application in applications:
        resources = []

        if application["status"] == "Rejected":
            reason = application["rejection_reason"] or "Other"
            resources = resource_map.get(
                reason,
                resource_map["Other"]
            )

        application_feedback.append({
            "application": application,
            "resources": resources
        })

    return render_template(
        "my_applications.html",
        application_feedback=application_feedback
    )
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)