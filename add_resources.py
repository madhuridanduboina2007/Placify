
import sqlite3

DATABASE = "database.db"

resources = [
    (
        "Technical Skills",
        "GeeksforGeeks DSA Practice",
        "Practise data structures and algorithms for technical placements.",
        "https://www.geeksforgeeks.org/practice-problems/gfg-160/",
        "Practice"
    ),
    (
        "Technical Skills",
        "W3Schools Programming Tutorials",
        "Revise programming fundamentals, Python, Java and SQL.",
        "https://www.w3schools.com/",
        "Learning"
    ),
    (
        "Aptitude",
        "IndiaBIX Aptitude",
        "Practise quantitative aptitude questions.",
        "https://www.indiabix.com/aptitude/",
        "Practice"
    ),
    (
        "Aptitude",
        "IndiaBIX Online Aptitude Tests",
        "Test your placement aptitude preparation.",
        "https://www.indiabix.com/online-test/aptitude-test/",
        "Practice"
    ),
    (
        "Communication",
        "British Council LearnEnglish",
        "Improve English communication and language skills.",
        "https://learnenglish.britishcouncil.org/",
        "Learning"
    ),
    (
        "Interview Performance",
        "GeeksforGeeks Interview Preparation",
        "Explore technical interview preparation resources.",
        "https://www.geeksforgeeks.org/",
        "Learning"
    ),
    (
        "Resume",
        "Harvard Resume Guide",
        "Learn how to prepare a clear and professional resume.",
        "https://careerservices.fas.harvard.edu/resources/create-a-resume-cv-or-cover-letter/",
        "Learning"
    ),
    (
        "Other",
        "GeeksforGeeks Placement Preparation",
        "Explore programming and placement preparation resources.",
        "https://www.geeksforgeeks.org/",
        "Learning"
    )
]

connection = sqlite3.connect(DATABASE)

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

for resource in resources:
    connection.execute(
        """
        INSERT INTO resources
            (topic, title, description, url, resource_type)
        SELECT ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM resources
            WHERE topic = ? AND title = ?
        )
        """,
        (*resource, resource[0], resource[1])
    )

connection.commit()
connection.close()

print("Improvement resources added successfully!")