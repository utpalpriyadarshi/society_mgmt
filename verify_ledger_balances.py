#!/usr/bin/env python3
"""
Verification script to check ledger debit, credit, and balance calculations in the main database.
This script verifies that the balances are calculated correctly for existing transactions.
"""

import sys
import os
import sqlite3

def verify_ledger_balances():
    """Verify ledger balances in the main database"""
    db_path = "society_management.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    try:
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
        
        print("Verifying ledger balances:")
        print("-" * 80)
        print("ID\tTxn ID\t\tDate\t\tType\t\tDebit\tCredit\tActual Bal\tCalc Bal\tStatus")
        print("-" * 80)
        
        calculated_balance = 0.0
        all_correct = True
        
        for row in rows:
            id, transaction_id, date, transaction_type, debit, credit, actual_balance = row
            
            # Calculate expected balance
            calculated_balance = calculated_balance + credit - debit
            expected_balance = calculated_balance
            
            # Check if actual balance matches calculated balance
            is_correct = abs(actual_balance - expected_balance) <= 0.01
            status = "OK" if is_correct else "ERROR"
            
            if not is_correct:
                all_correct = False
            
            print(f"{id}\t{transaction_id}\t{date}\t{transaction_type}\t\t{debit}\t{credit}\t{actual_balance}\t\t{expected_balance:.2f}\t\t{status}")
        
        print("-" * 80)
        if all_correct:
            print("SUCCESS: All ledger balances are calculated correctly!")
        else:
            print("ERROR: Some ledger balances are incorrect!")
            print("\nNote: If balances are incorrect, you can fix them by running:")
            print("  from models.ledger import LedgerManager")
            print("  ledger_manager = LedgerManager()")
            print("  ledger_manager.recalculate_balances()")
        
        return all_correct
            
    except Exception as e:
        print(f"Error checking ledger balances: {e}")
        return False

if __name__ == "__main__":
    verify_ledger_balances()