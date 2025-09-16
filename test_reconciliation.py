from models.bank_statement import ReconciliationManager
from models.ledger import LedgerManager
from datetime import datetime, timedelta

def test_reconciliation():
    \"\"\"Test the reconciliation functionality.\"\"\"
    try:
        print(\"Testing reconciliation functionality...\")
        
        # Initialize managers
        reconciliation_manager = ReconciliationManager()
        ledger_manager = LedgerManager()
        bank_manager = reconciliation_manager.bank_manager
        
        # Check current data
        print(\"\\n1. Checking current data:\")
        
        # Get ledger transactions
        ledger_transactions = ledger_manager.get_all_transactions()
        print(f\"   Total ledger transactions: {len(ledger_transactions)}\")
        
        # Get bank entries
        bank_entries = bank_manager.get_all_entries()
        print(f\"   Total bank entries: {len(bank_entries)}\")
        
        # Check if there are any reconciled items
        reconciled_ledger = [t for t in ledger_transactions if t.reconciliation_status == \"Reconciled\"]
        reconciled_bank = [e for e in bank_entries if e.reconciliation_status == \"Reconciled\"]
        print(f\"   Reconciled ledger transactions: {len(reconciled_ledger)}\")
        print(f\"   Reconciled bank entries: {len(reconciled_bank)}\")
        
        # Test finding matches for a recent date range
        end_date = datetime.now().strftime(\"%Y-%m-%d\")
        start_date = (datetime.now() - timedelta(days=30)).strftime(\"%Y-%m-%d\")
        
        print(f\"\\n2. Testing match finding for period {start_date} to {end_date}:\")
        matches = reconciliation_manager.find_matches(start_date, end_date)
        print(f\"   Found {len(matches)} potential matches\")
        
        if matches:
            print(\"   Top matches:\")
            for i, match in enumerate(matches[:3]):  # Show top 3 matches
                ledger_txn = match['ledger_transaction']
                bank_entry = match['bank_entry']
                confidence = match['confidence']
                print(f\"     {i+1}. {ledger_txn.transaction_id} <-> Bank entry {bank_entry.id} (Confidence: {confidence:.2f})\")
        
        # Test reconciliation summary
        print(f\"\\n3. Reconciliation summary for period {start_date} to {end_date}:\")
        summary = reconciliation_manager.get_reconciliation_summary(start_date, end_date)
        print(f\"   Ledger: {summary['ledger']}\")
        print(f\"   Bank: {summary['bank']}\")
        
        print(\"\\nReconciliation functionality test completed successfully!\")
        
    except Exception as e:
        print(f\"Error testing reconciliation functionality: {e}\")
        import traceback
        traceback.print_exc()

# Test reconciliation
test_reconciliation()