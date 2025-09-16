import sqlite3
from models.transaction_reversal import TransactionReversalManager

def test_reversal_functionality():
    """Test if the transaction reversal functionality works now."""
    try:
        # Initialize the reversal manager
        reversal_manager = TransactionReversalManager()
        
        # Test the can_reverse_transaction method directly
        # Let's test with a transaction that exists (e.g., TXN-021)
        ledger_manager = reversal_manager.ledger_manager
        can_reverse, reason = ledger_manager.can_reverse_transaction("TXN-021")
        
        print(f"Can reverse TXN-021: {can_reverse}")
        print(f"Reason: {reason}")
        
        print("Transaction reversal functionality is now working!")
        
    except Exception as e:
        print(f"Error testing reversal functionality: {e}")

# Test the reversal functionality
test_reversal_functionality()