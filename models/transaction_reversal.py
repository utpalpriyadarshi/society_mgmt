# models/transaction_reversal.py
import sqlite3
from datetime import datetime
from models.ledger import LedgerManager, LedgerTransaction
from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError
from utils.audit_logger import audit_logger
from utils.security import get_user_id

class ReversalReason:
    """Enumeration of valid reversal reasons"""
    ENTERED_IN_ERROR = "Entered in Error"
    DUPLICATE_ENTRY = "Duplicate Entry"
    WRONG_AMOUNT = "Wrong Amount"
    WRONG_ACCOUNT = "Wrong Account"
    WRONG_PERIOD = "Wrong Period"
    OTHER = "Other"

class TransactionReversal:
    def __init__(self, id, original_transaction_id, reversal_transaction_id, 
                 reason, remarks, reversed_by, reversed_at=None):
        self.id = id
        self.original_transaction_id = original_transaction_id
        self.reversal_transaction_id = reversal_transaction_id
        self.reason = reason
        self.remarks = remarks
        self.reversed_by = reversed_by
        self.reversed_at = reversed_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TransactionReversalManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.ledger_manager = LedgerManager(db_path)
        self.init_reversal_table()
    
    def init_reversal_table(self):
        """Initialize the transaction_reversals table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_reversals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_transaction_id TEXT UNIQUE,
            reversal_transaction_id TEXT,
            reason TEXT,
            remarks TEXT,
            reversed_by TEXT,
            reversed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (original_transaction_id) REFERENCES ledger(transaction_id),
            FOREIGN KEY (reversal_transaction_id) REFERENCES ledger(transaction_id)
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reversals_original ON transaction_reversals(original_transaction_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reversals_reversal ON transaction_reversals(reversal_transaction_id)')
        
        conn.commit()
        conn.close()
    
    def get_valid_reversal_reasons(self):
        """Get list of valid reversal reasons"""
        return [
            ReversalReason.ENTERED_IN_ERROR,
            ReversalReason.DUPLICATE_ENTRY,
            ReversalReason.WRONG_AMOUNT,
            ReversalReason.WRONG_ACCOUNT,
            ReversalReason.WRONG_PERIOD,
            ReversalReason.OTHER
        ]
    
    def reverse_transaction(self, original_transaction_id, reason, remarks, reversed_by):
        """
        Reverse a transaction by creating a new transaction with opposite values
        Returns the reversal transaction ID if successful, None otherwise
        """
        # Validate reason
        if reason not in self.get_valid_reversal_reasons():
            raise ValueError("Invalid reversal reason")
        
        # Check if transaction exists
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, transaction_id, date, flat_no, transaction_type, category, 
                       description, debit, credit, payment_mode, entered_by
                FROM ledger WHERE transaction_id = ?
            ''', (original_transaction_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError("Transaction not found")
            
            original_txn = LedgerTransaction(
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], 0.0, row[9], row[10]  # Balance set to 0 initially
            )
            
            # Check if transaction is already reversed
            cursor.execute('''
                SELECT id FROM transaction_reversals WHERE original_transaction_id = ?
            ''', (original_transaction_id,))
            
            if cursor.fetchone():
                raise ValueError("Transaction has already been reversed")
        
        # Create reversal transaction with opposite values
        reversal_type = "Payment Reversal" if original_txn.transaction_type == "Payment" else "Expense Reversal"
        # Include remarks in the transaction description if provided
        if remarks:
            reversal_description = f"REVERSAL: {original_txn.description} - {remarks}" if original_txn.description else f"REVERSAL - {remarks}"
        else:
            reversal_description = f"REVERSAL: {original_txn.description}" if original_txn.description else "REVERSAL"
        
        # Add the reversal transaction
        reversal_transaction_id = self.ledger_manager.add_transaction(
            datetime.now().strftime("%Y-%m-%d"),  # Today's date
            original_txn.flat_no,
            reversal_type,
            original_txn.category,
            reversal_description,
            original_txn.credit,  # Opposite of original
            original_txn.debit,   # Opposite of original
            original_txn.payment_mode,
            reversed_by
        )
        
        if not reversal_transaction_id:
            return None
        
        # Record the reversal in the reversals table
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transaction_reversals 
                (original_transaction_id, reversal_transaction_id, reason, remarks, reversed_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (original_transaction_id, reversal_transaction_id, reason, remarks, reversed_by))
            
            conn.commit()
            
            # Log the reversal action
            user_id = get_user_id(reversed_by) if reversed_by else None
            old_values = {
                'transaction_id': original_txn.transaction_id,
                'date': original_txn.date,
                'flat_no': original_txn.flat_no,
                'transaction_type': original_txn.transaction_type,
                'category': original_txn.category,
                'description': original_txn.description,
                'debit': original_txn.debit,
                'credit': original_txn.credit,
                'payment_mode': original_txn.payment_mode,
                'entered_by': original_txn.entered_by
            }
            
            new_values = {
                'reversal_transaction_id': reversal_transaction_id,
                'reversal_date': datetime.now().strftime("%Y-%m-%d"),
                'reversal_type': reversal_type,
                'reversal_description': reversal_description,
                'reversal_debit': original_txn.credit,
                'reversal_credit': original_txn.debit,
                'reason': reason,
                'remarks': remarks
            }
            
            audit_logger.log_data_change(
                user_id=user_id or -1,
                username=reversed_by or "Unknown",
                action="REVERSE_TRANSACTION",
                table_name="ledger",
                record_id=None,
                old_values=old_values,
                new_values=new_values
            )
        
        return reversal_transaction_id
    
    def get_reversal_by_original_transaction(self, original_transaction_id):
        """Get reversal record by original transaction ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, original_transaction_id, reversal_transaction_id, reason, remarks, reversed_by, reversed_at
            FROM transaction_reversals WHERE original_transaction_id = ?
        ''', (original_transaction_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return TransactionReversal(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6]
            )
        return None
    
    def get_all_reversals(self):
        """Get all transaction reversals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, original_transaction_id, reversal_transaction_id, reason, remarks, reversed_by, reversed_at
            FROM transaction_reversals ORDER BY reversed_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        reversals = []
        for row in rows:
            reversal = TransactionReversal(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6]
            )
            reversals.append(reversal)
        
        return reversals