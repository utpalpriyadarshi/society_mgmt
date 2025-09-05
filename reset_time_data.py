#!/usr/bin/env python3
"""
Script to reset time-related data in the society management system database.
This script can be run with command-line arguments for specific reset operations.

Usage:
  python reset_time_data.py [option]

Options:
  --unlock        Reset account lockout times only (unlock all accounts)
  --ledger-dates  Reset ledger dates to today
  --ledger-times  Reset ledger created timestamps to now
  --resident-dates Reset resident joining dates to today
  --all           Reset all time-related data
  --status        View current time data status
  --help          Show this help message
"""

import sqlite3
from datetime import datetime, timedelta
import os
import sys

def reset_account_lockout_times(db_path="society_management.db"):
    """Reset account lockout times for all users"""
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
        
        print(f"Successfully reset account lockout times for {rows_affected} user(s).")
        return True
        
    except Exception as e:
        print(f"Error resetting account lockout times: {e}")
        return False

def reset_ledger_dates(db_path="society_management.db", new_date=None):
    """Reset ledger transaction dates to a specific date or today"""
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    # Use provided date or today
    if new_date is None:
        new_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update all ledger dates
        cursor.execute("""
            UPDATE ledger 
            SET date = ?
        """, (new_date,))
        
        # Get number of affected rows
        rows_affected = cursor.rowcount
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"Successfully reset dates for {rows_affected} ledger transaction(s) to {new_date}.")
        return True
        
    except Exception as e:
        print(f"Error resetting ledger dates: {e}")
        return False

def reset_ledger_created_times(db_path="society_management.db"):
    """Reset ledger created_at timestamps to current time"""
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update all ledger created_at timestamps
        cursor.execute("""
            UPDATE ledger 
            SET created_at = CURRENT_TIMESTAMP
        """)
        
        # Get number of affected rows
        rows_affected = cursor.rowcount
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"Successfully reset created_at timestamps for {rows_affected} ledger transaction(s).")
        return True
        
    except Exception as e:
        print(f"Error resetting ledger created_at timestamps: {e}")
        return False

def reset_resident_joining_dates(db_path="society_management.db", new_date=None):
    """Reset resident joining dates to a specific date or today"""
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    # Use provided date or today
    if new_date is None:
        new_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update all resident joining dates
        cursor.execute("""
            UPDATE residents 
            SET date_joining = ?
        """, (new_date,))
        
        # Get number of affected rows
        rows_affected = cursor.rowcount
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"Successfully reset joining dates for {rows_affected} resident(s) to {new_date}.")
        return True
        
    except Exception as e:
        print(f"Error resetting resident joining dates: {e}")
        return False

def view_time_data_status(db_path="society_management.db"):
    """View current time-related data status"""
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\nCurrent Time-Related Data Status:")
        print("=" * 50)
        
        # Get ledger date range
        cursor.execute("""
            SELECT MIN(date), MAX(date), COUNT(*) 
            FROM ledger
        """)
        ledger_result = cursor.fetchone()
        if ledger_result[0]:
            print(f"Ledger Transactions: {ledger_result[2]}")
            print(f"  Date Range: {ledger_result[0]} to {ledger_result[1]}")
        else:
            print("Ledger Transactions: 0")
        
        # Get resident joining date range
        cursor.execute("""
            SELECT MIN(date_joining), MAX(date_joining), COUNT(*) 
            FROM residents
        """)
        resident_result = cursor.fetchone()
        if resident_result[0]:
            print(f"Residents: {resident_result[2]}")
            print(f"  Joining Date Range: {resident_result[0]} to {resident_result[1]}")
        else:
            print("Residents: 0")
        
        # Get user lockout status
        cursor.execute("""
            SELECT COUNT(*) 
            FROM users 
            WHERE locked_until IS NOT NULL 
            AND locked_until > datetime('now')
        """)
        locked_count = cursor.fetchone()[0]
        print(f"Locked User Accounts: {locked_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error viewing time data status: {e}")
        return False

def reset_all_time_data(db_path="society_management.db", new_date=None):
    """Reset all time-related data in the database"""
    print("Resetting all time-related data...")
    
    success = True
    success &= reset_account_lockout_times(db_path)
    success &= reset_ledger_dates(db_path, new_date)
    success &= reset_ledger_created_times(db_path)
    success &= reset_resident_joining_dates(db_path, new_date)
    
    if success:
        print("\nAll time-related data has been successfully reset!")
    else:
        print("\nSome errors occurred while resetting time-related data.")
    
    return success

def show_help():
    """Show help message"""
    print(__doc__)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
        show_help()
        return
    
    option = sys.argv[1]
    
    if option == "--unlock":
        reset_account_lockout_times()
    elif option == "--ledger-dates":
        reset_ledger_dates()
    elif option == "--ledger-times":
        reset_ledger_created_times()
    elif option == "--resident-dates":
        reset_resident_joining_dates()
    elif option == "--all":
        reset_all_time_data()
    elif option == "--status":
        view_time_data_status()
    else:
        print("Invalid option. Use --help for usage information.")

if __name__ == "__main__":
    main()