#!/usr/bin/env python3
"""
Test script for login security features
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.security import authenticate_user, hash_password
from utils.session_manager import session_manager

def test_bcrypt_hashing():
    """Test that bcrypt hashing works correctly"""
    print("Testing bcrypt hashing...")
    password = "testpassword123"
    hashed = hash_password(password)
    
    # Check that the hash starts with the bcrypt prefix
    if hashed.startswith(b'$2b$') or hashed.startswith(b'$2a$') or hashed.startswith(b'$2y$'):
        print("[PASS] Bcrypt hashing is working correctly")
        return True
    else:
        print("[FAIL] Bcrypt hashing is not working correctly")
        return False

def test_authentication():
    """Test user authentication"""
    print("\nTesting user authentication...")
    
    # Test with sysadmin user (default password should be 'systemadmin')
    result = authenticate_user("sysadmin", "systemadmin")
    if result:
        print("[PASS] Authentication successful for sysadmin")
        print(f"  User role: {result}")
        return True
    else:
        print("[FAIL] Authentication failed for sysadmin")
        return False

def test_failed_login_attempts():
    """Test failed login attempts tracking"""
    print("\nTesting failed login attempts tracking...")
    
    # First, let's reset any existing failed attempts for sysadmin
    conn = sqlite3.connect('society_management.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE username = 'sysadmin'")
    conn.commit()
    conn.close()
    
    # Try to login with wrong password
    result = authenticate_user("sysadmin", "wrongpassword")
    if not result:
        print("[PASS] Authentication correctly failed with wrong password")
    else:
        print("[FAIL] Authentication should have failed with wrong password")
        return False
    
    # Check if failed attempt was recorded
    conn = sqlite3.connect('society_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT failed_login_attempts FROM users WHERE username = 'sysadmin'")
    attempts = cursor.fetchone()[0]
    conn.close()
    
    if attempts == 1:
        print("[PASS] Failed login attempt was correctly recorded")
        return True
    else:
        print(f"[FAIL] Failed login attempt was not recorded correctly. Attempts: {attempts}")
        return False

def test_account_lockout():
    """Test account lockout after multiple failed attempts"""
    print("\nTesting account lockout...")
    
    # Reset any existing failed attempts
    conn = sqlite3.connect('society_management.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE username = 'sysadmin'")
    conn.commit()
    conn.close()
    
    # Fail login 5 times
    for i in range(5):
        authenticate_user("sysadmin", "wrongpassword")
    
    # Try to login with correct password now
    result = authenticate_user("sysadmin", "systemadmin")
    if not result:
        print("[PASS] Account is correctly locked after 5 failed attempts")
        
        # Check if account is locked in database
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT locked_until FROM users WHERE username = 'sysadmin'")
        locked_until = cursor.fetchone()[0]
        conn.close()
        
        if locked_until:
            print("[PASS] Lockout time is correctly set in database")
            return True
        else:
            print("[FAIL] Lockout time is not set in database")
            return False
    else:
        print("[FAIL] Account should be locked after 5 failed attempts")
        return False

def test_session_management():
    """Test session management"""
    print("\nTesting session management...")
    
    # Create a session for sysadmin
    session_id = session_manager.create_session("sysadmin")
    if session_id:
        print("[PASS] Session created successfully")
        print(f"  Session ID: {session_id}")
    else:
        print("[FAIL] Failed to create session")
        return False
    
    # Validate the session
    username = session_manager.validate_session(session_id)
    if username == "sysadmin":
        print("[PASS] Session validation successful")
        return True
    else:
        print("[FAIL] Session validation failed")
        return False

def main():
    """Run all tests"""
    print("Login Security Feature Tests")
    print("=" * 40)
    
    tests = [
        test_bcrypt_hashing,
        test_authentication,
        test_failed_login_attempts,
        test_account_lockout,
        test_session_management
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("All tests passed! Login security features are working correctly.")
    else:
        print("Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()