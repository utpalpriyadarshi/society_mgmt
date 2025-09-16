#!/usr/bin/env python3
"""
Test script to verify PDF import functionality in the reconciliation feature
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test PDF text parsing
def test_pdf_parsing():
    """Test the PDF text parsing functionality"""
    try:
        import fitz  # PyMuPDF
        
        # Read the sample PDF we created
        doc = fitz.open("sample_bank_statement.pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        print("PDF text extraction successful!")
        print("Extracted text:")
        print(text)
        
        # Test parsing the text
        from gui.reconciliation_tab import ReconciliationTab
        tab = ReconciliationTab()
        entries = tab.parse_pdf_text(text)
        
        print(f"\nParsed {len(entries)} entries from PDF:")
        for entry in entries:
            print(f"  Date: {entry['date']}, Description: {entry['description']}, Amount: {entry['amount']}")
            
        return len(entries) > 0
        
    except Exception as e:
        print(f"Error testing PDF parsing: {e}")
        return False

def test_import_functions():
    """Test that the import functions exist"""
    try:
        from gui.reconciliation_tab import ReconciliationTab
        tab = ReconciliationTab()
        
        # Check that the methods exist
        assert hasattr(tab, 'import_bank_statement')
        assert hasattr(tab, 'import_csv_statement')
        assert hasattr(tab, 'import_pdf_statement')
        assert hasattr(tab, 'parse_pdf_text')
        
        print("All import methods exist!")
        return True
    except Exception as e:
        print(f"Error testing import functions: {e}")
        return False

if __name__ == "__main__":
    print("Testing PDF import functionality...")
    
    # Test import functions
    if test_import_functions():
        print("PASS: Import functions test passed")
    else:
        print("FAIL: Import functions test failed")
    
    # Test PDF parsing
    if test_pdf_parsing():
        print("PASS: PDF parsing test passed")
    else:
        print("FAIL: PDF parsing test failed")
    
    print("PDF import testing completed!")