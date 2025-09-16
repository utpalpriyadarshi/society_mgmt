# Simple test for reconciliation functionality
import sqlite3
from datetime import datetime, timedelta

def simple_reconciliation_test():
    """Simple test for reconciliation functionality."""
    try:
        # Connect to database
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT COUNT(*) FROM ledger")
        ledger_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bank_statements")
        bank_count = cursor.fetchone()[0]
        
        print(f"Ledger transactions: {ledger_count}")
        print(f"Bank statements: {bank_count}")
        
        # Check reconciliation status
        cursor.execute("SELECT reconciliation_status, COUNT(*) FROM ledger GROUP BY reconciliation_status")
        ledger_status = cursor.fetchall()
        print(f"Ledger reconciliation status: {dict(ledger_status)}")
        
        cursor.execute("SELECT reconciliation_status, COUNT(*) FROM bank_statements GROUP BY reconciliation_status")
        bank_status = cursor.fetchall()
        print(f"Bank reconciliation status: {dict(bank_status)}")
        
        # Test a simple query that would be used in reconciliation
        cursor.execute("SELECT COUNT(*) FROM ledger l JOIN bank_statements b ON l.id = b.matched_ledger_id WHERE l.reconciliation_status = 'Reconciled'")
        matched_count = cursor.fetchone()[0]
        print(f"Matched transactions: {matched_count}")
        
        conn.close()
        print("Reconciliation functionality test completed successfully!")
        
    except Exception as e:
        print(f"Error in reconciliation test: {e}")

# Run the test
simple_reconciliation_test()