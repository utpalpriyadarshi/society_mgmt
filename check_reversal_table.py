import sqlite3

def check_reversal_table():
    """Check if the transaction_reversals table exists and its schema."""
    try:
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transaction_reversals'")
        result = cursor.fetchone()
        
        if result:
            print("transaction_reversals table exists: True")
            
            # Get table schema
            cursor.execute('PRAGMA table_info(transaction_reversals)')
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        else:
            print("transaction_reversals table exists: False")
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Check the reversal table
check_reversal_table()