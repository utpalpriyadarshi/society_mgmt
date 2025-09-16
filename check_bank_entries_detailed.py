import sqlite3

def check_bank_entries_detailed():
    \"\"\"Check detailed information about bank entries.\"\"\"
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, date, description, amount, balance, reference_number, 
                   import_date, reconciliation_status, matched_ledger_id
            FROM bank_statements
            ORDER BY date ASC
        ''')
        entries = cursor.fetchall()
        
        print('Bank statement entries:')
        print('ID\tDate\t\tDescription\t\t\tAmount\t\tStatus\t\tMatched Ledger')
        print('-' * 90)
        for entry in entries:
            print(f'{entry[0]}\t{entry[1]}\t{entry[2][:30]:<30}\t{entry[3]}\t\t{entry[7]:<12}\t{entry[8] or \"None\"}')
            
        # Check the date range of entries
        if entries:
            dates = [entry[1] for entry in entries]
            print(f'\nDate range: {min(dates)} to {max(dates)}')
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f\"Database error: {e}\")
    except Exception as e:
        print(f\"Error: {e}\")

# Check bank entries
check_bank_entries_detailed()