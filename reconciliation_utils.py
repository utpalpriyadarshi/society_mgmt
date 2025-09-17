"""
Reconciliation Utilities

Helper functions to improve the reconciliation experience
"""

from datetime import datetime
from difflib import SequenceMatcher

class ReconciliationUtils:
    """Utility class for enhanced reconciliation functionality"""
    
    @staticmethod
    def calculate_confidence_score(ledger_txn, bank_entry, date_tolerance=3, amount_tolerance=0.01):
        """
        Calculate a confidence score for a potential match (0.0 to 1.0)
        Higher scores indicate better matches
        """
        # Calculate effective amount (credit - debit)
        ledger_amount = ledger_txn.credit - ledger_txn.debit
        
        # Date proximity factor (0-1, closer dates get higher scores)
        ledger_date = datetime.strptime(ledger_txn.date, "%Y-%m-%d")
        bank_date = datetime.strptime(bank_entry.date, "%Y-%m-%d")
        date_diff = abs((ledger_date - bank_date).days)
        date_confidence = max(0, 1.0 - (date_diff / max(date_tolerance, 1)))
        
        # Amount exactness factor (0-1, exact matches get higher scores)
        amount_diff = abs(ledger_amount - bank_entry.amount)
        amount_confidence = max(0, 1.0 - (amount_diff / max(abs(ledger_amount), abs(bank_entry.amount), 0.01)))
        
        # Description similarity factor (0-1, similar descriptions get higher scores)
        desc_similarity = SequenceMatcher(
            None, 
            ledger_txn.description.lower() if ledger_txn.description else "",
            bank_entry.description.lower() if bank_entry.description else ""
        ).ratio()
        
        # Reference number match (bonus points for exact matches)
        ref_match_bonus = 0.2 if (
            ledger_txn.transaction_id == bank_entry.reference_number or
            (ledger_txn.description and bank_entry.reference_number and 
             ledger_txn.description.find(bank_entry.reference_number) != -1)
        ) else 0
        
        # Overall confidence (weighted average)
        confidence = (
            date_confidence * 0.4 +      # 40% weight to date
            amount_confidence * 0.4 +    # 40% weight to amount
            desc_similarity * 0.2 +      # 20% weight to description
            ref_match_bonus              # Bonus for reference matches
        )
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    @staticmethod
    def suggest_matches(ledger_transactions, bank_entries, date_tolerance=3, amount_tolerance=0.01, max_suggestions=10):
        """
        Suggest top potential matches between ledger transactions and bank entries
        """
        suggestions = []
        
        for ledger_txn in ledger_transactions:
            # Skip already reconciled transactions
            if ledger_txn.reconciliation_status != "Unreconciled":
                continue
                
            ledger_amount = ledger_txn.credit - ledger_txn.debit
            
            for bank_entry in bank_entries:
                # Skip already reconciled entries
                if bank_entry.reconciliation_status != "Unreconciled":
                    continue
                    
                # Quick pre-filter to avoid unnecessary calculations
                amount_diff = abs(ledger_amount - bank_entry.amount)
                if amount_diff > max(ledger_amount * 0.5, 1000):  # Rough filter
                    continue
                    
                # Calculate detailed confidence
                confidence = ReconciliationUtils.calculate_confidence_score(
                    ledger_txn, bank_entry, date_tolerance, amount_tolerance
                )
                
                # Only suggest matches with reasonable confidence
                if confidence > 0.3:  # Minimum 30% confidence
                    suggestions.append({
                        'ledger_transaction': ledger_txn,
                        'bank_entry': bank_entry,
                        'confidence': confidence,
                        'amount_diff': amount_diff,
                        'date_diff': abs((
                            datetime.strptime(ledger_txn.date, "%Y-%m-%d") - 
                            datetime.strptime(bank_entry.date, "%Y-%m-%d")
                        ).days)
                    })
        
        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return top suggestions
        return suggestions[:max_suggestions]
    
    @staticmethod
    def auto_match_high_confidence(ledger_transactions, bank_entries, min_confidence=0.8):
        """
        Automatically match transactions with high confidence
        Returns list of matched pairs
        """
        matches = []
        used_bank_entries = set()
        
        # Sort ledger transactions by date for consistent processing
        sorted_ledger = sorted(ledger_transactions, key=lambda x: x.date)
        
        for ledger_txn in sorted_ledger:
            # Skip already reconciled transactions
            if ledger_txn.reconciliation_status != "Unreconciled":
                continue
                
            ledger_amount = ledger_txn.credit - ledger_txn.debit
            best_match = None
            best_confidence = 0
            
            for bank_entry in bank_entries:
                # Skip already used or reconciled entries
                if bank_entry.id in used_bank_entries or bank_entry.reconciliation_status != "Unreconciled":
                    continue
                    
                # Calculate confidence
                confidence = ReconciliationUtils.calculate_confidence_score(
                    ledger_txn, bank_entry
                )
                
                # Track best match
                if confidence > best_confidence and confidence >= min_confidence:
                    best_confidence = confidence
                    best_match = bank_entry
            
            # If we found a good match, use it
            if best_match:
                matches.append({
                    'ledger_transaction': ledger_txn,
                    'bank_entry': best_match,
                    'confidence': best_confidence
                })
                used_bank_entries.add(best_match.id)
        
        return matches
    
    @staticmethod
    def format_currency(amount):
        """Format amount as currency"""
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def get_transaction_type_icon(transaction_type):
        """Return appropriate icon for transaction type"""
        icons = {
            'Payment': '💰',      # Money bag
            'Expense': '💳',      # Credit card
            'Payment Reversal': '↩️',  # Return arrow
            'Expense Reversal': '↩️'   # Return arrow
        }
        return icons.get(transaction_type, '📋')  # Default clipboard
    
    @staticmethod
    def get_reconciliation_status_color(status):
        """Return appropriate color for reconciliation status"""
        colors = {
            'Reconciled': '#4CAF50',    # Green
            'Unreconciled': '#F44336',  # Red
            'Pending': '#FF9800'        # Orange
        }
        return colors.get(status, '#9E9E9E')  # Default gray

# Example usage function
def demonstrate_utilities():
    """Demonstrate the utility functions"""
    print("Reconciliation Utilities Demo")
    print("=" * 40)
    
    # Example confidence calculation
    class MockTransaction:
        def __init__(self, date, credit, debit, description=""):
            self.date = date
            self.credit = credit
            self.debit = debit
            self.description = description
            self.reconciliation_status = "Unreconciled"
    
    class MockBankEntry:
        def __init__(self, date, amount, description="", reference_number=""):
            self.date = date
            self.amount = amount
            self.description = description
            self.reference_number = reference_number
            self.reconciliation_status = "Unreconciled"
            self.id = id(self)
    
    # Create example transactions
    ledger_txn = MockTransaction("2023-01-15", 500.0, 0.0, "Maintenance payment")
    bank_entry = MockBankEntry("2023-01-15", 500.0, "Maintenance payment A101")
    
    # Calculate confidence
    confidence = ReconciliationUtils.calculate_confidence_score(ledger_txn, bank_entry)
    print(f"Confidence score: {confidence:.2f}")
    
    # Format currency
    formatted = ReconciliationUtils.format_currency(1234.56)
    print(f"Formatted currency: {formatted}")
    
    # Get status color
    color = ReconciliationUtils.get_reconciliation_status_color("Reconciled")
    print(f"Reconciled color: {color}")

if __name__ == "__main__":
    demonstrate_utilities()