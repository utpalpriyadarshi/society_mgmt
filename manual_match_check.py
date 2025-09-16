# Manual match checking
import sqlite3
from datetime import datetime

def check_matches():
    conn = sqlite3.connect('society_management.db')
    c = conn.cursor()
    
    # Get ledger entries (Jan 2023)
    c.execute('SELECT id, transaction_id, date, debit, credit, description FROM ledger WHERE date BETWEEN "2023-01-01" AND "2023-02-28"')
    ledger_entries = c.fetchall()
    
    # Get bank entries (Jan-Feb 2023)
    c.execute('SELECT id, date, description, amount FROM bank_statements WHERE date BETWEEN "2023-01-01" AND "2023-02-28"')
    bank_entries = c.fetchall()
    
    print("Manual Match Analysis:")
    print("="*50)
    
    tolerance_days = 3
    tolerance_amount = 0.01
    
    matches = []
    
    for ledger in ledger_entries:
        ledger_id, txn_id, ledger_date, debit, credit, ledger_desc = ledger
        ledger_amount = credit - debit
        
        print(f"\nLedger: {txn_id} | Date: {ledger_date} | Amount: {ledger_amount} | Desc: {ledger_desc}")
        
        for bank in bank_entries:
            bank_id, bank_date, bank_desc, bank_amount = bank
            
            # Check amount match
            amount_diff = abs(ledger_amount - bank_amount)
            amount_match = amount_diff <= tolerance_amount
            
            # Check date match
            ledger_dt = datetime.strptime(ledger_date, "%Y-%m-%d")
            bank_dt = datetime.strptime(bank_date, "%Y-%m-%d")
            date_diff = abs((ledger_dt - bank_dt).days)
            date_match = date_diff <= tolerance_days
            
            if amount_match and date_match:
                confidence = (1.0 - (date_diff / tolerance_days)) * 0.6 + (1.0 - (amount_diff / max(abs(ledger_amount), abs(bank_amount), 0.01))) * 0.4
                print(f"  -> MATCH with Bank ID:{bank_id} | Date: {bank_date} | Amount: {bank_amount} | Conf: {confidence:.2f}")
                matches.append((txn_id, bank_id, confidence))
            else:
                print(f"  -> No match with Bank ID:{bank_id} | Date: {bank_date} | Amount: {bank_amount} | Date diff: {date_diff} days | Amount diff: {amount_diff}")
    
    print(f"\nTotal matches found: {len(matches)}")
    if matches:
        print("Matches:")
        for match in matches:
            print(f"  {match[0]} <-> Bank {match[1]} (Confidence: {match[2]:.2f})")
    
    conn.close()

check_matches()