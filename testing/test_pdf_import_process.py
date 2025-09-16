#!/usr/bin/env python3
"""
Test script to simulate PDF import process
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pdf_import_process():
    """Test the complete PDF import process"""
    print("Testing PDF Import Process")
    print("=" * 40)
    
    try:
        # Import required modules
        from models.bank_statement import BankStatementManager
        
        # Create bank statement manager
        bank_manager = BankStatementManager()
        
        # Test importing the sample PDF
        pdf_path = "sample_bank_statement.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"[ERROR] PDF file not found: {pdf_path}")
            return False
        
        print(f"Importing PDF: {pdf_path}")
        
        # Extract text from PDF
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        print(f"Extracted {len(text)} characters from PDF")
        
        # Parse the text (similar to what's done in reconciliation_tab.py)
        import re
        from datetime import datetime
        
        entries = []
        lines = text.split('\n')
        
        for line in lines:
            # Pattern 1: DD/MM/YYYY Description Amount
            pattern1 = r'(\\d{2}/\\d{2}/\\d{4})\\s+(.+?)\\s+(-?\\d+(?:,\\d{3})*(?:\\.\\d{2})?)'
            match1 = re.search(pattern1, line)
            
            # Pattern 2: DD-MM-YYYY Description Amount
            pattern2 = r'(\\d{2}-\\d{2}-\\d{4})\\s+(.+?)\\s+(-?\\d+(?:,\\d{3})*(?:\\.\\d{2})?)'
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
                        'balance': 0.0,
                        'reference_number': ''
                    })
                except Exception as e:
                    print(f"Error parsing line: {e}")
                    continue
            
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
                        'balance': 0.0,
                        'reference_number': ''
                    })
                except Exception as e:
                    print(f"Error parsing line: {e}")
                    continue
        
        print(f"Parsed {len(entries)} entries from PDF")
        
        # Try to import the entries
        print("Importing entries into database...")
        imported_count = bank_manager.import_statement(entries, "test_user")
        
        print(f"Successfully imported {imported_count} entries")
        
        # Check what's in the database
        print("\nChecking database contents...")
        all_entries = bank_manager.get_all_entries()
        print(f"Total entries in database: {len(all_entries)}")
        
        for entry in all_entries:
            print(f"  ID: {entry.id}, Date: {entry.date}, Description: {entry.description}, "
                  f"Amount: {entry.amount}, Status: {entry.reconciliation_status}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to test PDF import process: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pdf_import_process()