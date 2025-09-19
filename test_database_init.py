"""
Test script to verify database initialization
"""
import sqlite3
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from utils.db_context import get_db_connection

def test_database_initialization():
    print("Testing database initialization...")
    
    # Create a new database instance
    db = Database("test_society_management.db")
    
    # Check if the sysadmin user exists
    with get_db_connection("test_society_management.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users WHERE username = 'sysadmin'")
        result = cursor.fetchone()
        
        if result:
            username, role = result
            print(f"✓ Default user found: {username} ({role})")
            return True
        else:
            print("✗ Default user not found")
            return False

if __name__ == "__main__":
    try:
        success = test_database_initialization()
        if success:
            print("\nDatabase initialization test PASSED")
        else:
            print("\nDatabase initialization test FAILED")
    except Exception as e:
        print(f"\nDatabase initialization test FAILED with error: {e}")