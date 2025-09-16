import sqlite3

def check_all_transactions():
    """Check all transactions in the ledger, ordered by ID."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, transaction_id, date, description, debit, credit FROM ledger ORDER BY id')
        transactions = cursor.fetchall()
        
        print('All ledger transactions (ordered by ID):')
        print('ID\tTXN ID\t\tDate\t\tDescription\t\tDebit\t\tCredit')
        print('-' * 80)
        for txn in transactions:
            print(f'{txn[0]}\t{txn[1]}\t{txn[2]}\t{txn[3][:20]:<20}\t{txn[4]}\t\t{txn[5]}')
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check all transactions
check_all_transactions()