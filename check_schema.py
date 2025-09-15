import sqlite3

# Connect to the database
conn = sqlite3.connect('society_management.db')
cursor = conn.cursor()

# Get the schema for bank_statements table
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bank_statements'")
schema = cursor.fetchone()

if schema:
    print("Bank Statements Table Schema:")
    print(schema[0])
else:
    print("Bank statements table not found")

# Get the schema for reconciliation_history table
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reconciliation_history'")
schema = cursor.fetchone()

if schema:
    print("\nReconciliation History Table Schema:")
    print(schema[0])
else:
    print("\nReconciliation history table not found")

conn.close()