#!/usr/bin/env python3
"""
Interactive login test script
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.security import authenticate_user

def interactive_login():
    """Interactive login test"""
    print("Interactive Login Test")
    print("=" * 20)
    
    while True:
        username = input("\nUsername (or 'quit' to exit): ")
        if username.lower() == 'quit':
            break
            
        password = input("Password: ")
        
        # Try to authenticate
        user_role = authenticate_user(username, password)
        if user_role:
            print(f"\n[PASS] Login successful!")
            print(f"User: {username}")
            print(f"Role: {user_role}")
            
            # Check if account was locked and now unlocked
            print("\nYou can now access the system.")
        else:
            print(f"\n[FAIL] Login failed!")
            print("Invalid username or password.")
            
            # Check if account is locked
            import sqlite3
            conn = sqlite3.connect('society_management.db')
            cursor = conn.cursor()
            cursor.execute('''
            SELECT failed_login_attempts, locked_until FROM users WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                failed_attempts, locked_until = result
                print(f"Failed login attempts: {failed_attempts}")
                
                if locked_until:
                    from datetime import datetime
                    locked_time = datetime.fromisoformat(locked_until)
                    if datetime.now() < locked_time:
                        remaining_time = locked_time - datetime.now()
                        minutes = int(remaining_time.total_seconds() // 60)
                        print(f"Account is locked. Try again in {minutes} minutes.")
                    else:
                        print("Account is locked but lock has expired. Try again.")

if __name__ == "__main__":
    interactive_login()