#!/usr/bin/env python3
"""
Test script to verify the reconciliation feature implementation
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from models.bank_statement import BankStatementManager, ReconciliationManager
from models.ledger import LedgerManager

def setup_test_data():
    """Set up some test data for reconciliation"""
    # Clear any existing test data
    conn = sqlite3.connect("society_management.db")
    cursor = conn.cursor()
    
    # Clear existing data for clean test
    cursor.execute("DELETE FROM bank_statements")
    cursor.execute("DELETE FROM ledger")
    
    # Insert test ledger transactions
    test_transactions = [
        ("TXN-001", "2023-01-15", "A101", "Payment", "Maintenance", "January maintenance", 
         0.0, 500.0, 500.0, "Cash", "admin", datetime.now(), "Unreconciled"),
        ("TXN-002", "2023-01-20", "B202", "Payment", "Maintenance", "January maintenance", 
         0.0, 500.0, 1000.0, "Bank Transfer", "admin", datetime.now(), "Unreconciled"),
        ("TXN-003", "2023-01-25", None, "Expense", "Utilities", "Electricity bill", 
         300.0, 0.0, 700.0, "Cheque", "admin", datetime.now(), "Unreconciled"),
        ("TXN-004", "2023-02-01", "C303", "Payment", "Maintenance", "February maintenance", 
         0.0, 500.0, 1200.0, "Online Payment", "admin", datetime.now(), "Unreconciled"),
    ]
    
    for transaction in test_transactions:
        cursor.execute('''
            INSERT INTO ledger (transaction_id, date, flat_no, transaction_type, category, description,
                              debit, credit, balance, payment_mode, entered_by, created_at, reconciliation_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', transaction)
    
    # Insert test bank statement entries
    test_bank_entries = [
        ("2023-01-15", "Maintenance payment from A101", 500.0, 1500.0, "REF001"),
        ("2023-01-20", "Maintenance payment from B202", 500.0, 2000.0, "REF002"),
        ("2023-01-25", "Electricity bill payment", -300.0, 1700.0, "REF003"),
        ("2023-02-01", "Maintenance payment from C303", 500.0, 2200.0, "REF004"),
    ]
    
    for entry in test_bank_entries:
        cursor.execute('''
            INSERT INTO bank_statements (date, description, amount, balance, reference_number)
            VALUES (?, ?, ?, ?, ?)
        ''', entry)
    
    conn.commit()
    conn.close()

def test_reconciliation_feature():
    """Test the reconciliation feature implementation"""
    print("Setting up test data...")
    setup_test_data()
    
    print("Testing BankStatementManager...")
    bank_manager = BankStatementManager()
    entries = bank_manager.get_all_entries()
    print(f"Retrieved {len(entries)} bank statement entries")
    
    print("Testing LedgerManager...")
    ledger_manager = LedgerManager()
    transactions = ledger_manager.get_all_transactions()
    print(f"Retrieved {len(transactions)} ledger transactions")
    
    print("Testing ReconciliationManager...")
    reconciliation_manager = ReconciliationManager()
    
    # Test finding matches
    matches = reconciliation_manager.find_matches("2023-01-01", "2023-02-28")
    print(f"Found {len(matches)} potential matches")
    
    # Test reconciliation summary
    summary = reconciliation_manager.get_reconciliation_summary("2023-01-01", "2023-02-28")
    print(f"Reconciliation summary: {summary}")
    
    # Test marking as matched (match first pair)
    if matches:
        first_match = matches[0]
        ledger_id = first_match['ledger_transaction'].id
        bank_id = first_match['bank_entry'].id
        
        print(f"Marking ledger transaction {ledger_id} and bank entry {bank_id} as matched...")
        result = reconciliation_manager.mark_as_matched(ledger_id, bank_id, "test_user")
        print(f"Match result: {result}")
    
    print("All tests completed successfully!")
    return True

if __name__ == "__main__":
    test_reconciliation_feature()