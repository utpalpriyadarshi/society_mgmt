"""
Test authentication with new hash
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from utils.security import authenticate_user
from utils.db_context import get_db_connection
import bcrypt

def test_new_hash():
    print("Testing new bcrypt hash...")
    
    # Test password and new hash
    password = "systemadmin"
    stored_hash = "$2b$12$ks61E9uJb/7v42mQw3thnu7xxVyv6iKBRU2jUPRWZzeD/oQRVOHqK"
    
    print(f"Password: {password}")
    print(f"Stored hash: {stored_hash}")
    
    # Test bcrypt verification
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    
    result = bcrypt.checkpw(password_bytes, hash_bytes)
    print(f"bcrypt.checkpw result: {result}")
    
    if result:
        print("Bcrypt verification SUCCESSFUL")
    else:
        print("Bcrypt verification FAILED")

def test_authentication():
    print("\nTesting authentication with new hash...")
    
    # Create a test database with the new hash
    with get_db_connection("test_auth.db") as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TEXT
        )
        ''')
        
        # Insert sysadmin user with new hash
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("sysadmin", "$2b$12$ks61E9uJb/7v42mQw3thnu7xxVyv6iKBRU2jUPRWZzeD/oQRVOHqK", "System Admin")
        )
        
        conn.commit()
        
        # Test authentication
        # We need to patch the get_db_connection to use our test database
        import utils.db_context
        original_get_db_connection = utils.db_context.get_db_connection
        
        def test_get_db_connection(*args, **kwargs):
            return original_get_db_connection("test_auth.db", *args[1:], **kwargs)
        
        utils.db_context.get_db_connection = test_get_db_connection
        
        try:
            result = authenticate_user("sysadmin", "systemadmin", "127.0.0.1", "test-session")
            
            if result:
                print(f"Authentication SUCCESSFUL! Role: {result}")
            else:
                print("Authentication FAILED!")
                
                # Check why it failed
                cursor.execute("SELECT failed_login_attempts, locked_until FROM users WHERE username = 'sysadmin'")
                result = cursor.fetchone()
                
                if result:
                    failed_attempts, locked_until = result
                    print(f"Failed attempts: {failed_attempts}")
                    print(f"Locked until: {locked_until}")
        finally:
            # Restore original function
            utils.db_context.get_db_connection = original_get_db_connection

if __name__ == "__main__":
    test_new_hash()
    test_authentication()