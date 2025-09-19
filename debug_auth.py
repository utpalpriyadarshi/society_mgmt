"""
Debug script to test authentication directly
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from utils.security import authenticate_user
from utils.db_context import get_db_connection
from database import Database

def debug_authentication():
    print("Debugging authentication process...")
    
    # Initialize database
    print("Initializing database...")
    db = Database("debug_society_management.db")
    
    # Check if sysadmin user exists
    print("Checking for sysadmin user...")
    with get_db_connection("debug_society_management.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, password_hash FROM users WHERE username = 'sysadmin'")
        result = cursor.fetchone()
        
        if result:
            username, role, password_hash = result
            print(f"User found: {username} ({role})")
            print(f"Password hash: {password_hash}")
            print(f"Hash type: {'bcrypt' if password_hash.startswith('$2b$') or password_hash.startswith('$2a$') or password_hash.startswith('$2y$') else 'sha256' if len(password_hash) == 64 else 'unknown'}")
        else:
            print("Sysadmin user NOT found!")
            return
    
    # Test authentication
    print("\nTesting authentication...")
    result = authenticate_user("sysadmin", "systemadmin", "127.0.0.1", "debug-session")
    
    if result:
        print(f"Authentication SUCCESSFUL! Role: {result}")
    else:
        print("Authentication FAILED!")
        
        # Check why it failed
        with get_db_connection("debug_society_management.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT failed_login_attempts, locked_until FROM users WHERE username = 'sysadmin'")
            result = cursor.fetchone()
            
            if result:
                failed_attempts, locked_until = result
                print(f"Failed attempts: {failed_attempts}")
                print(f"Locked until: {locked_until}")

if __name__ == "__main__":
    debug_authentication()
