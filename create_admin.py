from database import get_db_connection

connection = get_db_connection()

username = "admin"
password = "admin123"

# Check whether admin already exists
admin = connection.execute(
    "SELECT * FROM admins WHERE username = ?",
    (username,)
).fetchone()

if admin:

    connection.execute(
        """
        UPDATE admins
        SET password = ?
        WHERE username = ?
        """,
        (password, username)
    )

    print("Admin account password has been reset successfully!")

else:

    connection.execute(
        """
        INSERT INTO admins (username, password)
        VALUES (?, ?)
        """,
        (username, password)
    )

    print("Admin account created successfully!")

connection.commit()
connection.close()

print()
print("Username: admin")
print("Password: admin123")