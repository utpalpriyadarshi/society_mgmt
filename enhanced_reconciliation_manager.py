"""
Enhanced Reconciliation Manager

Extended functionality for better reconciliation experience
"""

import sqlite3
from datetime import datetime, timedelta
from models.ledger import LedgerManager
from models.bank_statement import BankStatementManager
from reconciliation_utils import ReconciliationUtils

class EnhancedReconciliationManager:
    """Enhanced reconciliation manager with improved matching and suggestions"""
    
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.ledger_manager = LedgerManager(db_path)
        self.bank_manager = BankStatementManager(db_path)
        
    def find_enhanced_matches(self, start_date, end_date, date_tolerance=3, amount_tolerance=0.01):
        """
        Find potential matches with enhanced confidence scoring
        """
        # Get ledger transactions in date range
        ledger_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        
        # Get bank statement entries in date range (with buffer for tolerance)
        start_buffer = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=date_tolerance)).strftime("%Y-%m-%d")
        end_buffer = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=date_tolerance)).strftime("%Y-%m-%d")
        
        bank_entries = self.bank_manager.get_entries_by_date_range(start_buffer, end_buffer)
        
        matches = []
        
        for ledger_txn in ledger_transactions:
            # Calculate effective amount (credit - debit)
            ledger_amount = ledger_txn.credit - ledger_txn.debit
            
            for bank_entry in bank_entries:
                # Check if already matched
                if bank_entry.reconciliation_status != "Unreconciled":
                    continue
                
                # Enhanced matching with detailed confidence calculation
                confidence = ReconciliationUtils.calculate_confidence_score(
                    ledger_txn, bank_entry, date_tolerance, amount_tolerance
                )
                
                # Only include matches with some confidence
                if confidence > 0.1:  # Minimum 10% confidence
                    matches.append({
                        'ledger_transaction': ledger_txn,
                        'bank_entry': bank_entry,
                        'confidence': confidence,
                        'ledger_amount': ledger_amount,
                        'bank_amount': bank_entry.amount
                    })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches
    
    def get_smart_suggestions(self, start_date, end_date, max_suggestions=10):
        """
        Get smart suggestions for potential matches
        """
        ledger_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        bank_entries = self.bank_manager.get_all_entries()  # Get all for better suggestions
        
        return ReconciliationUtils.suggest_matches(
            ledger_transactions, bank_entries, max_suggestions=max_suggestions
        )
    
    def auto_match_transactions(self, start_date, end_date, min_confidence=0.8):
        """
        Automatically match high-confidence transactions
        """
        ledger_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        bank_entries = self.bank_manager.get_all_entries()
        
        matches = ReconciliationUtils.auto_match_high_confidence(
            ledger_transactions, bank_entries, min_confidence
        )
        
        # Apply the matches to the database
        matched_count = 0
        for match in matches:
            ledger_txn = match['ledger_transaction']
            bank_entry = match['bank_entry']
            
            if self.mark_as_matched(ledger_txn.id, bank_entry.id):
                matched_count += 1
        
        return matched_count, len(matches)
    
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
    
    def get_enhanced_summary(self, start_date, end_date):
        """Get an enhanced reconciliation summary with more details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get detailed ledger summary
        cursor.execute('''
            SELECT reconciliation_status, COUNT(*), SUM(credit - debit) as net_amount
            FROM ledger 
            WHERE date BETWEEN ? AND ?
            GROUP BY reconciliation_status
        ''', (start_date, end_date))
        
        ledger_summary = {}
        ledger_amounts = {}
        for status, count, net_amount in cursor.fetchall():
            ledger_summary[status] = count
            ledger_amounts[status] = net_amount or 0
        
        # Get detailed bank statement summary
        cursor.execute('''
            SELECT reconciliation_status, COUNT(*), SUM(amount) as total_amount
            FROM bank_statements 
            WHERE date BETWEEN ? AND ?
            GROUP BY reconciliation_status
        ''', (start_date, end_date))
        
        bank_summary = {}
        bank_amounts = {}
        for status, count, total_amount in cursor.fetchall():
            bank_summary[status] = count
            bank_amounts[status] = total_amount or 0
        
        # Get recent reconciliation history
        cursor.execute('''
            SELECT user, notes, reconciliation_date
            FROM reconciliation_history
            WHERE reconciliation_date BETWEEN ? AND ?
            ORDER BY reconciliation_date DESC
            LIMIT 5
        ''', (start_date, end_date))
        
        recent_activity = cursor.fetchall()
        
        conn.close()
        
        return {
            'ledger': {
                'count': ledger_summary,
                'amount': ledger_amounts
            },
            'bank': {
                'count': bank_summary,
                'amount': bank_amounts
            },
            'recent_activity': recent_activity
        }
    
    def get_matching_statistics(self, start_date, end_date):
        """Get statistics about matching patterns"""
        matches = self.find_enhanced_matches(start_date, end_date)
        
        if not matches:
            return {
                'total_matches': 0,
                'avg_confidence': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0
            }
        
        confidences = [match['confidence'] for match in matches]
        avg_confidence = sum(confidences) / len(confidences)
        
        high_confidence = len([c for c in confidences if c >= 0.8])
        medium_confidence = len([c for c in confidences if 0.5 <= c < 0.8])
        low_confidence = len([c for c in confidences if c < 0.5])
        
        return {
            'total_matches': len(matches),
            'avg_confidence': round(avg_confidence, 2),
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence
        }

# Example usage
def demo_enhanced_manager():
    """Demonstrate the enhanced reconciliation manager"""
    print("Enhanced Reconciliation Manager Demo")
    print("=" * 40)
    
    manager = EnhancedReconciliationManager()
    
    # Example date range
    start_date = "2023-01-01"
    end_date = "2023-01-31"
    
    # Get enhanced summary
    summary = manager.get_enhanced_summary(start_date, end_date)
    print("Enhanced Summary:")
    print(f"  Ledger - Reconciled: {summary['ledger']['count'].get('Reconciled', 0)}")
    print(f"  Bank - Reconciled: {summary['bank']['count'].get('Reconciled', 0)}")
    
    # Get matching statistics
    stats = manager.get_matching_statistics(start_date, end_date)
    print(f"\nMatching Statistics:")
    print(f"  Total matches: {stats['total_matches']}")
    print(f"  Average confidence: {stats['avg_confidence']}")

if __name__ == "__main__":
    demo_enhanced_manager()