import sqlite3

def check_recent_transactions():
    """Check the most recent transactions in the ledger."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT transaction_id, date, description, debit, credit FROM ledger ORDER BY date DESC, id DESC LIMIT 10')
        transactions = cursor.fetchall()
        
        print('Recent ledger transactions:')
        for txn in transactions:
            print(f'  {txn[0]} - {txn[1]} - {txn[2]} - Debit: {txn[3]}, Credit: {txn[4]}')
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check recent transactions
check_recent_transactions()