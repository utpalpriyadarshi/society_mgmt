import sqlite3

def check_transaction_details():
    """Check detailed information about specific transactions."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        # Check TXN-019 and TXN-020 in detail
        for txn_id in ['TXN-019', 'TXN-020']:
            cursor.execute('SELECT * FROM ledger WHERE transaction_id = ?', (txn_id,))
            transaction = cursor.fetchone()
            
            if transaction:
                print(f'Details for {txn_id}:')
                columns = ['id', 'transaction_id', 'date', 'flat_no', 'transaction_type', 'category', 
                          'description', 'debit', 'credit', 'balance', 'payment_mode', 'entered_by', 
                          'created_at', 'reconciliation_status']
                for i, value in enumerate(transaction):
                    print(f'  {columns[i]}: {value}')
                print()
            else:
                print(f'{txn_id} not found in the ledger')
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check transaction details
check_transaction_details()