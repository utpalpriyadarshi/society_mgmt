import sqlite3

# Connect to the database
conn = sqlite3.connect('test_society_management.db')
cursor = conn.cursor()

# Check if users table exists and has data
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("Users table exists")
        cursor.execute("SELECT username, role FROM users;")
        users = cursor.fetchall()
        
        if users:
            print("Users in database:")
            for user in users:
                print(f"  - {user[0]} ({user[1]})")
        else:
            print("No users found in database")
    else:
        print("Users table does not exist")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()