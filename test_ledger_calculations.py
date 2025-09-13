#!/usr/bin/env python3
"""
Test script to verify ledger debit, credit, and balance calculations.
This script tests various transaction scenarios to ensure correct accounting.
"""

import sys
import os
import sqlite3

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'ai_agent_utils'))

from models.ledger import LedgerManager

def setup_test_database():
    """Set up a test database with required tables"""
    test_db = "test_ledger_calculations.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Create the database file
    conn = sqlite3.connect(test_db)
    conn.close()
    
    # Apply migrations to the test database
    from ai_agent_utils.migrations.migration_manager import MigrationManager
    migration_manager = MigrationManager(test_db, os.path.join(project_root, 'ai_agent_utils', 'migrations'))
    migration_manager.apply_pending_migrations()
    
    return test_db

def test_ledger_calculations():
    """Test ledger calculations with various transaction scenarios"""
    print("Testing ledger debit, credit, and balance calculations...")
    
    # Set up test database
    test_db = setup_test_database()
    
    try:
        # Initialize ledger manager with test database
        ledger_manager = LedgerManager(test_db)
        
        # Test Case 1: Starting balance should be 0.0
        print("\n1. Testing initial balance:")
        transactions = ledger_manager.get_all_transactions()
        if transactions:
            print(f"   ERROR: Expected no transactions, found {len(transactions)}")
            return False
        else:
            print("   SUCCESS: No transactions as expected")
        
        # Test Case 2: Add a payment (credit to society)
        print("\n2. Adding a payment transaction (credit to society):")
        txn_id1 = ledger_manager.add_transaction(
            date="2023-01-01",
            flat_no="A101",
            transaction_type="Payment",
            category="Maintenance",
            description="January maintenance payment",
            debit=0.0,
            credit=500.0,
            payment_mode="Cash",
            entered_by="test_user"
        )
        
        if not txn_id1:
            print("   ERROR: Failed to add payment transaction")
            return False
        else:
            print(f"   SUCCESS: Added payment transaction {txn_id1}")
        
        # Check the balance after payment
        transactions = ledger_manager.get_all_transactions()
        if len(transactions) != 1:
            print(f"   ERROR: Expected 1 transaction, found {len(transactions)}")
            return False
            
        txn1 = transactions[0]
        expected_balance = 500.0  # Credit increases balance
        if abs(txn1.balance - expected_balance) > 0.01:
            print(f"   ERROR: Expected balance {expected_balance}, got {txn1.balance}")
            return False
        else:
            print(f"   SUCCESS: Balance is correct ({txn1.balance})")
        
        # Test Case 3: Add an expense (debit from society)
        print("\n3. Adding an expense transaction (debit from society):")
        txn_id2 = ledger_manager.add_transaction(
            date="2023-01-02",
            flat_no=None,
            transaction_type="Expense",
            category="Utilities",
            description="Electricity bill",
            debit=200.0,
            credit=0.0,
            payment_mode="Bank Transfer",
            entered_by="test_user"
        )
        
        if not txn_id2:
            print("   ERROR: Failed to add expense transaction")
            return False
        else:
            print(f"   SUCCESS: Added expense transaction {txn_id2}")
        
        # Check the balance after expense
        transactions = ledger_manager.get_all_transactions()
        if len(transactions) != 2:
            print(f"   ERROR: Expected 2 transactions, found {len(transactions)}")
            return False
            
        txn2 = transactions[1]  # Second transaction
        expected_balance = 500.0 - 200.0  # Previous balance minus debit
        if abs(txn2.balance - expected_balance) > 0.01:
            print(f"   ERROR: Expected balance {expected_balance}, got {txn2.balance}")
            print(f"   Previous balance: {transactions[0].balance}")
            return False
        else:
            print(f"   SUCCESS: Balance is correct ({txn2.balance})")
        
        # Test Case 4: Add another payment
        print("\n4. Adding another payment transaction:")
        txn_id3 = ledger_manager.add_transaction(
            date="2023-01-03",
            flat_no="B202",
            transaction_type="Payment",
            category="Maintenance",
            description="January maintenance payment",
            debit=0.0,
            credit=600.0,
            payment_mode="Online Payment",
            entered_by="test_user"
        )
        
        if not txn_id3:
            print("   ERROR: Failed to add payment transaction")
            return False
        else:
            print(f"   SUCCESS: Added payment transaction {txn_id3}")
        
        # Check the balance after second payment
        transactions = ledger_manager.get_all_transactions()
        if len(transactions) != 3:
            print(f"   ERROR: Expected 3 transactions, found {len(transactions)}")
            return False
            
        txn3 = transactions[2]  # Third transaction
        expected_balance = 300.0 + 600.0  # Previous balance plus credit
        if abs(txn3.balance - expected_balance) > 0.01:
            print(f"   ERROR: Expected balance {expected_balance}, got {txn3.balance}")
            print(f"   Previous balance: {transactions[1].balance}")
            return False
        else:
            print(f"   SUCCESS: Balance is correct ({txn3.balance})")
        
        # Print all transactions for verification
        print("\n5. Final transaction summary:")
        print("ID\tTxn ID\t\tDate\t\tType\t\tDebit\tCredit\tBalance")
        print("-" * 70)
        for txn in transactions:
            print(f"{txn.id}\t{txn.transaction_id}\t{txn.date}\t{txn.transaction_type}\t\t{txn.debit}\t{txn.credit}\t{txn.balance}")
        
        print("\nSUCCESS: All ledger calculations are correct!")
        return True
        
    except Exception as e:
        print(f"ERROR: Unexpected error during testing: {e}")
        return False
    finally:
        # Clean up test database
        try:
            if os.path.exists(test_db):
                os.remove(test_db)
        except:
            # Ignore cleanup errors on Windows
            pass

if __name__ == "__main__":
    success = test_ledger_calculations()
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)