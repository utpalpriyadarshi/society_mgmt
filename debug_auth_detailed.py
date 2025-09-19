"""
Detailed debug of authenticate_user function
"""
import sys
import os
import bcrypt

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from utils.db_context import get_db_connection

def debug_authenticate_user(username, password, ip_address=None, session_id=None):
    print(f"Debug authenticate_user called with:")
    print(f"  username: {username}")
    print(f"  password: {password}")
    print(f"  ip_address: {ip_address}")
    print(f"  session_id: {session_id}")
    
    # Check if the user is locked out
    with get_db_connection("test_auth.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, failed_login_attempts, locked_until FROM users WHERE username = ?
        ''', (username,))
        
        lockout_result = cursor.fetchone()
        
        if lockout_result:
            user_id, failed_attempts, locked_until = lockout_result
            print(f"User found in lockout check: id={user_id}, failed_attempts={failed_attempts}, locked_until={locked_until}")
            
            # Check if the account is locked
            if locked_until:
                from datetime import datetime
                try:
                    locked_time = datetime.fromisoformat(locked_until)
                    if datetime.now() < locked_time:
                        print("Account is locked!")
                        return None  # Account is locked
                except Exception as e:
                    print(f"Error parsing locked_until: {e}")
        else:
            print("User not found in lockout check")
    
    # Proceed with authentication
    with get_db_connection("test_auth.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, password_hash, role FROM users WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        
        if result:
            user_id, stored_hash, user_role = result
            print(f"User found in auth check: id={user_id}, role={user_role}")
            print(f"Stored hash: {stored_hash}")
            print(f"Hash type: {type(stored_hash)}")
            
            # Handle both bytes and string password hashes
            # Convert to bytes if it's a string
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
                print("Converted hash to bytes")
            
            print(f"Hash after conversion: {stored_hash}")
            
            # Check if the stored hash is a bcrypt hash (starts with $2b$, $2a$, or $2y$)
            is_bcrypt = isinstance(stored_hash, bytes) and (stored_hash.startswith(b'$2b$') or 
                       stored_hash.startswith(b'$2a$') or 
                       stored_hash.startswith(b'$2y$'))
            print(f"Is bcrypt hash: {is_bcrypt}")
            
            if is_bcrypt:
                print("Using bcrypt verification")
                # New bcrypt hash
                password_encoded = password.encode('utf-8')
                print(f"Password encoded: {password_encoded}")
                
                try:
                    bcrypt_result = bcrypt.checkpw(password_encoded, stored_hash)
                    print(f"bcrypt.checkpw result: {bcrypt_result}")
                    
                    if bcrypt_result:
                        print("Authentication SUCCESSFUL!")
                        return user_role
                    else:
                        print("Authentication FAILED - password mismatch")
                except Exception as e:
                    print(f"Error during bcrypt verification: {e}")
            else:
                print("Not a bcrypt hash")
        else:
            print("User not found in auth check")
            
        return None

def test_debug_auth():
    print("Testing debug authentication...")
    
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
            "INSERT OR REPLACE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("sysadmin", "$2b$12$ks61E9uJb/7v42mQw3thnu7xxVyv6iKBRU2jUPRWZzeD/oQRVOHqK", "System Admin")
        )
        
        conn.commit()
    
    # Test authentication
    result = debug_authenticate_user("sysadmin", "systemadmin", "127.0.0.1", "test-session")
    
    if result:
        print(f"\nFinal result: Authentication SUCCESSFUL! Role: {result}")
    else:
        print(f"\nFinal result: Authentication FAILED!")

if __name__ == "__main__":
    test_debug_auth()