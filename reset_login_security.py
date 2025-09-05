#!/usr/bin/env python3
"""
Script to reset login security for all users in the society management system.
This will reset failed login attempts and unlock any locked accounts.
"""

import sqlite3
from datetime import datetime
import os

def reset_login_security(db_path="society_management.db"):
    """Reset login security for all users"""
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Reset failed login attempts and locked_until for all users
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = 0, 
                locked_until = NULL
        """)
        
        # Get number of affected rows
        rows_affected = cursor.rowcount
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"Successfully reset login security for {rows_affected} user(s).")
        print("All accounts are now unlocked and can be used for login.")
        return True
        
    except Exception as e:
        print(f"Error resetting login security: {e}")
        return False

def view_user_security_status(db_path="society_management.db"):
    """View current security status of all users"""
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user security information
        cursor.execute("""
            SELECT username, role, failed_login_attempts, locked_until 
            FROM users
        """)
        
        users = cursor.fetchall()
        
        print("\nCurrent User Security Status:")
        print("-" * 80)
        print(f"{'Username':<15} {'Role':<15} {'Failed Attempts':<15} {'Locked Until':<20}")
        print("-" * 80)
        
        for user in users:
            username, role, failed_attempts, locked_until = user
            locked_until_display = locked_until if locked_until else "Not locked"
            print(f"{username:<15} {role:<15} {failed_attempts:<15} {locked_until_display:<20}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error viewing user security status: {e}")
        return False

if __name__ == "__main__":
    print("Society Management System - Login Security Reset Tool")
    print("=" * 50)
    
    # First, show current status
    view_user_security_status()
    
    # Reset login security without asking for confirmation
    print("\n" + "=" * 50)
    print("Resetting login security for all users...")
    if reset_login_security():
        print("\nLogin security has been successfully reset!")
        print("\nUpdated status:")
        view_user_security_status()
    else:
        print("\nFailed to reset login security.")