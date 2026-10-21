import sqlite3

DATABASE = "database.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = get_db_connection()

    # ---------------- ADMIN TABLE ----------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)


    # ---------------- STUDENTS TABLE ----------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            cgpa REAL NOT NULL,
            password TEXT NOT NULL
        )
    """)


    # ---------------- COMPANIES TABLE ----------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            location TEXT,
            website TEXT
        )
    """)


    # ---------------- JOBS TABLE ----------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            description TEXT,
            required_cgpa REAL NOT NULL,
            salary REAL,
            deadline TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
        # ---------------- ADD REQUIRED SKILLS TO JOBS ----------------
    try:
        connection.execute("""
            ALTER TABLE jobs
            ADD COLUMN required_skills TEXT
        """)
    except sqlite3.OperationalError:
        # Column already exists
        pass

 # ---------------- ADD SKILLS TO STUDENTS ----------------
    try:
        connection.execute("""
            ALTER TABLE students
            ADD COLUMN skills TEXT
        """)
    except sqlite3.OperationalError:
       pass   

 # ---------------- ADD REQUIRED DEPARTMENT TO JOBS ----------------
    try:
       connection.execute("""
           ALTER TABLE jobs
           ADD COLUMN required_department TEXT
     """)
    except sqlite3.OperationalError:
        pass 

 # ---------------- ADD REQUIRED YEAR TO JOBS ----------------
    try:
       connection.execute("""
           ALTER TABLE jobs
           ADD COLUMN required_year TEXT
       """)
    except sqlite3.OperationalError:
        pass     
    # ---------------- APPLICATIONS TABLE ----------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            application_date TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)


    # Safely add rejection feedback columns to existing applications table

    try:
        connection.execute("""
            ALTER TABLE applications
            ADD COLUMN rejection_reason TEXT
        """)
    except sqlite3.OperationalError as error:
        if "duplicate column name" not in str(error).lower():
            raise

    try:
        connection.execute("""
            ALTER TABLE applications
            ADD COLUMN admin_feedback TEXT
        """)
    except sqlite3.OperationalError as error:
        if "duplicate column name" not in str(error).lower():
            raise
    
    # Resources for student improvement recommendations
    connection.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)    

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")