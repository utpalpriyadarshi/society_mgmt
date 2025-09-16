import sqlite3

def check_specific_transactions():
    """Check for specific transaction IDs in the ledger."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        # Check for TXN-19 and TXN-20 specifically
        for txn_id in ['TXN-19', 'TXN-20']:
            cursor.execute('SELECT transaction_id, date, description, debit, credit FROM ledger WHERE transaction_id = ?', (txn_id,))
            transaction = cursor.fetchone()
            
            if transaction:
                print(f'Found {txn_id}: {transaction[1]} - {transaction[2]} - Debit: {transaction[3]}, Credit: {transaction[4]}')
            else:
                print(f'{txn_id} not found in the ledger')
                
        # Also check for transactions with ID 19 and 20
        for txn_num in [19, 20]:
            txn_id = f'TXN-{txn_num:03d}'  # Format as TXN-019, TXN-020
            cursor.execute('SELECT transaction_id, date, description, debit, credit FROM ledger WHERE transaction_id = ?', (txn_id,))
            transaction = cursor.fetchone()
            
            if transaction:
                print(f'Found {txn_id}: {transaction[1]} - {transaction[2]} - Debit: {transaction[3]}, Credit: {transaction[4]}')
            else:
                print(f'{txn_id} not found in the ledger')
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check for specific transactions
check_specific_transactions()