# models/bank_statement.py
import sqlite3
from datetime import datetime

class BankStatementEntry:
    def __init__(self, id, date, description, amount, balance, reference_number, 
                 import_date=None, reconciliation_status="Unreconciled", matched_ledger_id=None):
        self.id = id
        self.date = date
        self.description = description
        self.amount = amount
        self.balance = balance
        self.reference_number = reference_number
        self.import_date = import_date
        self.reconciliation_status = reconciliation_status
        self.matched_ledger_id = matched_ledger_id

class BankStatementManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def import_statement(self, entries, user=None):
        """
        Import bank statement entries
        entries: list of dictionaries with keys: date, description, amount, balance, reference_number
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            imported_count = 0
            for entry in entries:
                # Check if entry already exists (based on date, description, and amount)
                cursor.execute('''
                    SELECT id FROM bank_statements 
                    WHERE date = ? AND description = ? AND amount = ?
                ''', (entry['date'], entry['description'], entry['amount']))
                
                existing_entry = cursor.fetchone()
                
                if not existing_entry:
                    # Only insert if it doesn't already exist
                    cursor.execute('''
                        INSERT INTO bank_statements (date, description, amount, balance, reference_number)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (entry['date'], entry['description'], entry['amount'], entry['balance'], entry['reference_number']))
                    imported_count += 1
            
            if imported_count > 0:
                # Record in reconciliation history
                cursor.execute('''
                    INSERT INTO reconciliation_history (user, notes)
                    VALUES (?, ?)
                ''', (user or "System", f"Imported {imported_count} bank statement entries"))
            
            conn.commit()
            conn.close()
            return imported_count
        except Exception as e:
            conn.close()
            print(f"Error importing bank statement: {e}")
            return 0
    
    def get_all_entries(self, limit=None):
        """Retrieve all bank statement entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute('''
                SELECT id, date, description, amount, balance, reference_number, 
                       import_date, reconciliation_status, matched_ledger_id
                FROM bank_statements
                ORDER BY date ASC, id ASC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, date, description, amount, balance, reference_number, 
                       import_date, reconciliation_status, matched_ledger_id
                FROM bank_statements
                ORDER BY date ASC, id ASC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entry = BankStatementEntry(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
            )
            entries.append(entry)
        
        return entries
    
    def get_entries_by_date_range(self, start_date, end_date):
        """Retrieve bank statement entries within a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, date, description, amount, balance, reference_number, 
                   import_date, reconciliation_status, matched_ledger_id
            FROM bank_statements
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC, id ASC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entry = BankStatementEntry(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
            )
            entries.append(entry)
        
        return entries
    
    def update_reconciliation_status(self, entry_id, status, matched_ledger_id=None):
        """Update the reconciliation status of a bank statement entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if matched_ledger_id:
            cursor.execute('''
                UPDATE bank_statements 
                SET reconciliation_status = ?, matched_ledger_id = ?
                WHERE id = ?
            ''', (status, matched_ledger_id, entry_id))
        else:
            cursor.execute('''
                UPDATE bank_statements 
                SET reconciliation_status = ?
                WHERE id = ?
            ''', (status, entry_id))
        
        conn.commit()
        conn.close()
        return True

class ReconciliationManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.ledger_manager = None
        self.bank_manager = BankStatementManager(db_path)
        
        # Import here to avoid circular imports
        from models.ledger import LedgerManager
        self.ledger_manager = LedgerManager(db_path)
    
    def find_matches(self, start_date, end_date, tolerance_days=3, tolerance_amount=0.01):
        """
        Find potential matches between ledger transactions and bank statement entries
        Returns a list of potential matches with confidence scores
        """
        # Get ledger transactions in date range
        ledger_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        
        # Get bank statement entries in date range (with buffer for tolerance)
        from datetime import datetime, timedelta
        start_buffer = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=tolerance_days)).strftime("%Y-%m-%d")
        end_buffer = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=tolerance_days)).strftime("%Y-%m-%d")
        
        bank_entries = self.bank_manager.get_entries_by_date_range(start_buffer, end_buffer)
        
        matches = []
        
        for ledger_txn in ledger_transactions:
            # Calculate effective amount (credit - debit)
            ledger_amount = ledger_txn.credit - ledger_txn.debit
            
            for bank_entry in bank_entries:
                # Check if already matched
                if bank_entry.reconciliation_status != "Unreconciled":
                    continue
                
                # Check amount match (within tolerance)
                if abs(ledger_amount - bank_entry.amount) <= tolerance_amount:
                    # Check date match (within tolerance days)
                    ledger_date = datetime.strptime(ledger_txn.date, "%Y-%m-%d")
                    bank_date = datetime.strptime(bank_entry.date, "%Y-%m-%d")
                    date_diff = abs((ledger_date - bank_date).days)
                    
                    if date_diff <= tolerance_days:
                        # Calculate confidence score (higher is better)
                        # Date proximity factor (0-1, closer dates get higher scores)
                        date_confidence = 1.0 - (date_diff / tolerance_days)
                        
                        # Amount exactness factor (0-1, exact matches get higher scores)
                        amount_diff = abs(ledger_amount - bank_entry.amount)
                        amount_confidence = 1.0 - (amount_diff / max(abs(ledger_amount), abs(bank_entry.amount), 0.01))
                        
                        # Overall confidence (weighted average)
                        confidence = (date_confidence * 0.6) + (amount_confidence * 0.4)
                        
                        matches.append({
                            'ledger_transaction': ledger_txn,
                            'bank_entry': bank_entry,
                            'confidence': confidence,
                            'date_diff': date_diff,
                            'amount_diff': amount_diff
                        })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches
    
    def mark_as_matched(self, ledger_id, bank_entry_id, user=None):
        """Mark a ledger transaction and bank entry as matched"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update ledger transaction
            cursor.execute('''
                UPDATE ledger 
                SET reconciliation_status = 'Reconciled'
                WHERE id = ?
            ''', (ledger_id,))
            
            # Update bank entry
            cursor.execute('''
                UPDATE bank_statements 
                SET reconciliation_status = 'Reconciled', matched_ledger_id = ?
                WHERE id = ?
            ''', (ledger_id, bank_entry_id))
            
            # Record in reconciliation history
            cursor.execute('''
                INSERT INTO reconciliation_history (user, notes)
                VALUES (?, ?)
            ''', (user or "System", f"Matched ledger transaction {ledger_id} with bank entry {bank_entry_id}"))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error marking as matched: {e}")
            return False
    
    def get_reconciliation_summary(self, start_date, end_date):
        """Get a summary of reconciliation status for a period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get ledger summary
        cursor.execute('''
            SELECT reconciliation_status, COUNT(*) 
            FROM ledger 
            WHERE date BETWEEN ? AND ?
            GROUP BY reconciliation_status
        ''', (start_date, end_date))
        
        ledger_summary = dict(cursor.fetchall())
        
        # Get bank statement summary
        cursor.execute('''
            SELECT reconciliation_status, COUNT(*) 
            FROM bank_statements 
            WHERE date BETWEEN ? AND ?
            GROUP BY reconciliation_status
        ''', (start_date, end_date))
        
        bank_summary = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'ledger': ledger_summary,
            'bank': bank_summary
        }