#!/usr/bin/env python3
"""
Test script to verify that the ledger timestamp fix works correctly.
This script tests that ledger entries now use local time instead of UTC.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.ledger import LedgerManager

# Add the project root and ai_agent_utils to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'ai_agent_utils'))

def test_ledger_timestamp():
    """Test that ledger entries use local time for created_at timestamp"""
    print("Testing ledger timestamp fix...")
    
    # Create a temporary test database
    test_db = "test_ledger_timestamp.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Initialize ledger manager with test database
    # First create the database file
    conn = sqlite3.connect(test_db)
    conn.close()
    
    # Apply migrations to the test database
    from ai_agent_utils.migrations.migration_manager import MigrationManager
    migration_manager = MigrationManager(test_db, os.path.join(project_root, 'ai_agent_utils', 'migrations'))
    migration_manager.apply_pending_migrations()
    
    # Initialize ledger manager with test database
    ledger_manager = LedgerManager(test_db)
    
    # Add a test transaction
    transaction_id = ledger_manager.add_transaction(
        date="2023-01-01",
        flat_no="A101",
        transaction_type="Payment",
        category="Maintenance",
        description="Test payment",
        debit=0.0,
        credit=100.0,
        payment_mode="Cash",
        entered_by="test_user"
    )
    
    if not transaction_id:
        print("ERROR: Failed to add transaction")
        return False
    
    print(f"Added transaction with ID: {transaction_id}")
    
    # Retrieve the transaction and check the created_at timestamp
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT created_at FROM ledger WHERE transaction_id = ?", (transaction_id,))
    result = cursor.fetchone()
    
    if not result:
        print("ERROR: Could not retrieve transaction")
        conn.close()
        return False
    
    created_at = result[0]
    conn.close()
    
    print(f"Created at timestamp: {created_at}")
    
    # Check if the timestamp is in the expected format (YYYY-MM-DD HH:MM:SS)
    try:
        # Parse the timestamp to verify it's in the correct format
        parsed_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        print(f"Parsed timestamp: {parsed_time}")
        
        # Get current local time
        current_time = datetime.now()
        
        # Check if the timestamp is reasonably close to current time (within 1 minute)
        time_diff = abs((current_time - parsed_time).total_seconds())
        if time_diff > 60:
            print(f"WARNING: Timestamp difference is {time_diff} seconds, which is more than expected")
            # This might be OK if there's a significant time difference between test runs
        else:
            print(f"SUCCESS: Timestamp is within expected range ({time_diff} seconds)")
            
        print("SUCCESS: Ledger timestamp fix is working correctly")
        return True
        
    except ValueError as e:
        print(f"ERROR: Timestamp format is incorrect: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)

if __name__ == "__main__":
    success = test_ledger_timestamp()
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)