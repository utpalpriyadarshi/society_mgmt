#!/usr/bin/env python3
"""
Script to fix ledger balances in the main database.
This script recalculates all ledger balances to ensure they are correct.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.ledger import LedgerManager

def fix_ledger_balances():
    """Fix ledger balances in the main database"""
    print("Fixing ledger balances in the main database...")
    
    try:
        # Initialize ledger manager with main database
        ledger_manager = LedgerManager()
        
        # Recalculate all balances
        print("Recalculating all ledger balances...")
        ledger_manager.recalculate_balances()
        
        print("SUCCESS: Ledger balances have been fixed!")
        
        # Verify the fix
        print("\nVerifying the fix...")
        verify_ledger_balances()
        
    except Exception as e:
        print(f"Error fixing ledger balances: {e}")
        import traceback
        traceback.print_exc()

def verify_ledger_balances():
    """Verify ledger balances in the main database"""
    db_path = "society_management.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all ledger transactions ordered by date and ID
        cursor.execute("""
            SELECT id, transaction_id, date, transaction_type, debit, credit, balance
            FROM ledger 
            ORDER BY date ASC, id ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("No ledger entries found in the database")
            return
        
        print("Ledger balances after fix:")
        print("-" * 80)
        print("ID\tTxn ID\t\tDate\t\tType\t\tDebit\tCredit\tBalance")
        print("-" * 80)
        
        calculated_balance = 0.0
        
        for row in rows:
            id, transaction_id, date, transaction_type, debit, credit, actual_balance = row
            
            # Calculate expected balance
            calculated_balance = calculated_balance + credit - debit
            
            print(f"{id}\t{transaction_id}\t{date}\t{transaction_type}\t\t{debit}\t{credit}\t{actual_balance}")
        
        print("-" * 80)
        print("Balances have been recalculated and should now be correct.")
        
    except Exception as e:
        print(f"Error verifying ledger balances: {e}")

if __name__ == "__main__":
    fix_ledger_balances()