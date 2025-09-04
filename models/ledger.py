# models/ledger.py
import sqlite3
from datetime import datetime

class LedgerTransaction:
    def __init__(self, id, transaction_id, date, flat_no, transaction_type, category, 
                 description, debit, credit, balance, payment_mode, entered_by, created_at=None):
        self.id = id
        self.transaction_id = transaction_id
        self.date = date
        self.flat_no = flat_no
        self.transaction_type = transaction_type
        self.category = category
        self.description = description
        self.debit = debit
        self.credit = credit
        self.balance = balance
        self.payment_mode = payment_mode
        self.entered_by = entered_by
        self.created_at = created_at

class LedgerManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def generate_transaction_id(self):
        """Generate a new transaction ID in the format TXN-001, TXN-002, etc."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM ledger')
        count = cursor.fetchone()[0]
        conn.close()
        
        return f"TXN-{count + 1:03d}"
    
    def add_transaction(self, date, flat_no, transaction_type, category, description,
                       debit, credit, payment_mode, entered_by):
        """
        Add a new transaction to the ledger following proper accounting procedures
        Returns the transaction ID if successful, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate transaction ID
            transaction_id = self.generate_transaction_id()
            
            # Calculate running balance
            cursor.execute('SELECT balance FROM ledger ORDER BY id DESC LIMIT 1')
            last_balance_row = cursor.fetchone()
            last_balance = last_balance_row[0] if last_balance_row else 0.0
            
            new_balance = last_balance + credit - debit
            
            cursor.execute('''
                INSERT INTO ledger (transaction_id, date, flat_no, transaction_type, category, description,
                                   debit, credit, balance, payment_mode, entered_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction_id, date, flat_no, transaction_type, category, description,
                  debit, credit, new_balance, payment_mode, entered_by))
            
            conn.commit()
            conn.close()
            return transaction_id
        except Exception as e:
            conn.close()
            print(f"Error adding transaction: {e}")
            return None
    
    def get_all_transactions(self, limit=None):
        """Retrieve all transactions in chronological order, optionally limited"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute('''
                SELECT id, transaction_id, date, flat_no, transaction_type, category, description,
                       debit, credit, balance, payment_mode, entered_by, created_at
                FROM ledger
                ORDER BY date ASC, id ASC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, transaction_id, date, flat_no, transaction_type, category, description,
                       debit, credit, balance, payment_mode, entered_by, created_at
                FROM ledger
                ORDER BY date ASC, id ASC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transaction = LedgerTransaction(
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], row[9], row[10], row[11], row[12]
            )
            transactions.append(transaction)
        
        return transactions
    
    def get_transactions_by_flat(self, flat_no):
        """Retrieve transactions for a specific flat in chronological order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, transaction_id, date, flat_no, transaction_type, category, description,
                   debit, credit, balance, payment_mode, entered_by, created_at
            FROM ledger
            WHERE flat_no = ?
            ORDER BY date ASC, id ASC
        ''', (flat_no,))
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transaction = LedgerTransaction(
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], row[9], row[10], row[11], row[12]
            )
            transactions.append(transaction)
        
        return transactions
    
    def get_transactions_by_date_range(self, start_date, end_date):
        """Retrieve transactions within a date range in chronological order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, transaction_id, date, flat_no, transaction_type, category, description,
                   debit, credit, balance, payment_mode, entered_by, created_at
            FROM ledger
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC, id ASC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transaction = LedgerTransaction(
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], row[9], row[10], row[11], row[12]
            )
            transactions.append(transaction)
        
        return transactions
    
    def get_payment_categories(self):
        """Get predefined payment categories"""
        return ["Maintenance", "Advertisement", "Donation", "Parking", "Other Income"]
    
    def get_expense_categories(self):
        """Get predefined expense categories"""
        return ["Utilities", "Salary", "AMC", "Security", "Repairs", "Miscellaneous", "Other Expenses"]
    
    def get_payment_modes(self):
        """Get predefined payment modes"""
        return ["Cash", "Bank Transfer", "Cheque", "Online Payment", "Other"]
    
    def delete_transaction(self, transaction_id):
        """
        Delete a transaction by transaction ID (for draft/unposted entries only)
        NOTE: This should only be used for draft entries that haven't been finalized.
        For posted transactions, use reverse_transaction instead.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if transaction exists
        cursor.execute('SELECT COUNT(*) FROM ledger WHERE transaction_id = ?', (transaction_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            raise ValueError("Transaction not found")
        
        # Check if transaction has been reversed
        cursor.execute('SELECT COUNT(*) FROM transaction_reversals WHERE original_transaction_id = ?', (transaction_id,))
        reversed_count = cursor.fetchone()[0]
        
        if reversed_count > 0:
            conn.close()
            raise ValueError("Cannot delete a transaction that has been reversed")
        
        # Log the deletion in a separate audit table (to be implemented)
        # For now, we'll just delete the transaction
        cursor.execute('DELETE FROM ledger WHERE transaction_id = ?', (transaction_id,))
        
        # Recalculate balances after deletion
        self.recalculate_balances()
        
        conn.commit()
        conn.close()
        return True
    
    def recalculate_balances(self):
        """Recalculate all balances after a deletion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, debit, credit FROM ledger ORDER BY date ASC, id ASC')
        transactions = cursor.fetchall()
        
        balance = 0.0
        for txn_id, debit, credit in transactions:
            balance = balance + credit - debit
            cursor.execute('UPDATE ledger SET balance = ? WHERE id = ?', (balance, txn_id))
        
        conn.commit()
        conn.close()
    
    def can_reverse_transaction(self, transaction_id):
        """
        Check if a transaction can be reversed
        Returns (can_reverse: bool, reason: str)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if transaction exists
        cursor.execute('SELECT COUNT(*) FROM ledger WHERE transaction_id = ?', (transaction_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            return False, "Transaction not found"
        
        # Check if transaction has already been reversed
        cursor.execute('SELECT COUNT(*) FROM transaction_reversals WHERE original_transaction_id = ?', (transaction_id,))
        reversed_count = cursor.fetchone()[0]
        
        if reversed_count > 0:
            conn.close()
            return False, "Transaction has already been reversed"
        
        conn.close()
        return True, "OK"