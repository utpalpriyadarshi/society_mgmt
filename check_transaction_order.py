import sqlite3

def check_transaction_order():
    """Check transaction order and verify TXN-019 and TXN-020 are present."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        # Get all transactions ordered by date (as displayed in the application)
        cursor.execute('''
            SELECT id, transaction_id, date, description, debit, credit 
            FROM ledger 
            ORDER BY date ASC, id ASC
        ''')
        transactions = cursor.fetchall()
        
        print("All transactions ordered by date (as displayed in application):")
        print("ID\tTXN ID\t\tDate\t\tDescription\t\tDebit\t\tCredit")
        print("-" * 80)
        for txn in transactions:
            print(f"{txn[0]}\t{txn[1]}\t{txn[2]}\t{txn[3][:20]:<20}\t{txn[4]}\t\t{txn[5]}")
            
        # Check specifically for TXN-019 and TXN-020
        print("\n" + "="*50)
        print("Checking for specific transactions:")
        
        for txn_id in ['TXN-019', 'TXN-020']:
            cursor.execute('''
                SELECT id, transaction_id, date, description, debit, credit 
                FROM ledger 
                WHERE transaction_id = ?
            ''', (txn_id,))
            transaction = cursor.fetchone()
            
            if transaction:
                print(f"FOUND {txn_id}: ID={transaction[0]}, Date={transaction[2]}, "
                      f"Description='{transaction[3]}', Debit={transaction[4]}, Credit={transaction[5]}")
            else:
                print(f"{txn_id} NOT FOUND in database")
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check transaction order
check_transaction_order()