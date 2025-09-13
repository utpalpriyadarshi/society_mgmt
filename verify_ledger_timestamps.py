#!/usr/bin/env python3
"""
Verification script to check ledger timestamps in the main database.
This script shows the created_at timestamps for recent ledger entries.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_ledger_timestamps():
    """Check the timestamps of ledger entries in the main database"""
    db_path = "society_management.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the 5 most recent ledger entries
        cursor.execute("""
            SELECT transaction_id, date, created_at, description 
            FROM ledger 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("No ledger entries found in the database")
            return
        
        print("Recent ledger entries and their timestamps:")
        print("-" * 80)
        for row in rows:
            transaction_id, date, created_at, description = row
            print(f"Transaction ID: {transaction_id}")
            print(f"  Date: {date}")
            print(f"  Created At: {created_at}")
            print(f"  Description: {description[:50]}{'...' if len(description) > 50 else ''}")
            print()
            
    except Exception as e:
        print(f"Error checking ledger timestamps: {e}")

if __name__ == "__main__":
    check_ledger_timestamps()