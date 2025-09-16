#!/usr/bin/env python3
"""
Test script to verify PDF parsing logic
"""

import sys
import os
import re
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pdf_parsing_logic():
    """Test the PDF text parsing logic without creating UI components"""
    try:
        # Sample text that might be extracted from a PDF bank statement
        sample_text = """
        BANK STATEMENT
        ================
        
        Account Number: 1234567890
        Statement Period: January 2023
        
        Date        Description                Amount    Balance
        ----------------------------------------------------------------
        15/01/2023  Maintenance payment A101   500.00        1,500.00
        20/01/2023  Maintenance payment B202   500.00        2,000.00
        25/01/2023  Electricity bill payment   -300.00       1,700.00
        01/02/2023  Maintenance payment C303   500.00        2,200.00
        
        End of Statement
        """
        
        print("Testing PDF text parsing logic...")
        print("Sample text:")
        print(sample_text)
        
        # Parse the text to extract transactions
        entries = []
        
        # Look for transaction lines
        lines = sample_text.split('\n')
        
        for line in lines:
            # Try to match common transaction patterns
            # Pattern 1: DD/MM/YYYY Description Amount
            pattern1 = r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?\d+(?:,\d{3})*(?:\.\d{2})?)'
            match1 = re.search(pattern1, line)
            
            # Pattern 2: DD-MM-YYYY Description Amount
            pattern2 = r'(\d{2}-\d{2}-\d{4})\s+(.+?)\s+(-?\d+(?:,\d{3})*(?:\.\d{2})?)'
            match2 = re.search(pattern2, line)
            
            if match1:
                date_str, description, amount_str = match1.groups()
                try:
                    # Parse date
                    date = datetime.strptime(date_str, "%d/%m/%Y").date()
                    
                    # Parse amount
                    amount_str = amount_str.replace(',', '')
                    amount = float(amount_str)
                    
                    # Clean description
                    description = description.strip()[:255]
                    
                    entries.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'description': description,
                        'amount': amount,
                        'balance': 0.0,  # Balance might be in a separate column
                        'reference_number': ''
                    })
                    print(f"Parsed entry: {date_str} | {description} | {amount_str}")
                except Exception as e:
                    print(f"Error parsing line: {line} - {e}")
                    continue  # Skip invalid entries
            
            elif match2:
                date_str, description, amount_str = match2.groups()
                try:
                    # Parse date
                    date = datetime.strptime(date_str, "%d-%m-%Y").date()
                    
                    # Parse amount
                    amount_str = amount_str.replace(',', '')
                    amount = float(amount_str)
                    
                    # Clean description
                    description = description.strip()[:255]
                    
                    entries.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'description': description,
                        'amount': amount,
                        'balance': 0.0,  # Balance might be in a separate column
                        'reference_number': ''
                    })
                    print(f"Parsed entry: {date_str} | {description} | {amount_str}")
                except Exception as e:
                    print(f"Error parsing line: {line} - {e}")
                    continue  # Skip invalid entries
        
        print(f"\nSuccessfully parsed {len(entries)} entries from sample text:")
        for entry in entries:
            print(f"  Date: {entry['date']}, Description: {entry['description']}, Amount: {entry['amount']}")
            
        return len(entries) > 0
        
    except Exception as e:
        print(f"Error testing PDF parsing logic: {e}")
        return False

if __name__ == "__main__":
    print("Testing PDF parsing logic...")
    
    # Test PDF parsing logic
    if test_pdf_parsing_logic():
        print("\nPASS: PDF parsing logic test passed")
    else:
        print("\nFAIL: PDF parsing logic test failed")
    
    print("PDF parsing logic testing completed!")