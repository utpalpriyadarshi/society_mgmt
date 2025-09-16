import sqlite3

def check_bank_tables():
    """Check bank-related tables in the database."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%bank%'")
        tables = cursor.fetchall()
        
        print('Bank-related tables:')
        for table in tables:
            print(f'  - {table[0]}')
            
        # Also check the bank_statements table specifically
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bank_statements'")
        bank_table = cursor.fetchone()
        
        if bank_table:
            print(f'\nBank statements table exists: {bank_table[0]}')
            
            # Check the schema
            cursor.execute('PRAGMA table_info(bank_statements)')
            columns = cursor.fetchall()
            print('Columns:')
            for col in columns:
                print(f'  {col[1]} ({col[2]})')
                
            # Check if there are any entries
            cursor.execute('SELECT COUNT(*) FROM bank_statements')
            count = cursor.fetchone()[0]
            print(f'\nNumber of bank statement entries: {count}')
        else:
            print('\nBank statements table does not exist')
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check bank tables
check_bank_tables()