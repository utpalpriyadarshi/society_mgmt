import sqlite3

# Connect to the database
conn = sqlite3.connect('society_management.db')
cursor = conn.cursor()

# Get the schema for the users table
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
schema = cursor.fetchone()

if schema:
    print("Users table schema:")
    print(schema[0])
else:
    print("Users table not found")

conn.close()