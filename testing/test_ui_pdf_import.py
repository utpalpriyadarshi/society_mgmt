#!/usr/bin/env python3
"""
Targeted diagnostic script to identify PDF import failure in UI
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ui_pdf_import():
    """Test the exact PDF import process as used in the UI"""
    print("Testing UI PDF Import Process")
    print("=" * 40)
    
    try:
        # Simulate what happens in reconciliation_tab.py import_pdf_statement method
        pdf_path = "sample_bank_statement.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"[ERROR] PDF file not found: {pdf_path}")
            return False
        
        print(f"Testing import of: {pdf_path}")
        
        # Step 1: Check if PyMuPDF is available (as done in UI)
        try:
            import fitz  # PyMuPDF
            print("[PASS] PyMuPDF imported successfully")
        except ImportError as e:
            print(f"[FAIL] PyMuPDF import failed: {e}")
            print("Please install with: pip install PyMuPDF")
            return False
        except Exception as e:
            print(f"[FAIL] PyMuPDF error: {e}")
            return False
        
        # Step 2: Extract text from PDF (as done in UI)
        try:
            print("Extracting text from PDF...")
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            print(f"[PASS] Text extracted: {len(text)} characters")
            
            if len(text.strip()) == 0:
                print("[WARNING] No text content found in PDF")
                print("This might be an image-only PDF which requires OCR")
                return False
                
        except Exception as e:
            print(f"[FAIL] Error extracting text from PDF: {e}")
            return False
        
        # Step 3: Parse the text (exact copy of parse_pdf_text method)
        try:
            print("Parsing extracted text...")
            import re
            from datetime import datetime
            
            entries = []
            
            # This is the EXACT parsing logic from reconciliation_tab.py
            lines = text.split('\n')
            
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
                        print(f"  Parsed: {date_str} | {description} | {amount_str}")
                    except Exception as e:
                        print(f"  Error parsing line: {line} - {e}")
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
                        print(f"  Parsed: {date_str} | {description} | {amount_str}")
                    except Exception as e:
                        print(f"  Error parsing line: {line} - {e}")
                        continue  # Skip invalid entries
            
            print(f"[PASS] Parsed {len(entries)} entries from PDF")
            
        except Exception as e:
            print(f"[FAIL] Error parsing PDF text: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 4: Try to import entries (as done in UI)
        try:
            print("Importing entries into database...")
            from models.bank_statement import BankStatementManager
            bank_manager = BankStatementManager()
            
            if len(entries) > 0:
                imported_count = bank_manager.import_statement(entries, "diagnostic_test")
                print(f"[RESULT] Import result: {imported_count} entries imported")
                
                if imported_count == 0:
                    print("[INFO] No new entries imported (they may already exist)")
                
                # Check what's in the database
                print("Checking database contents...")
                all_entries = bank_manager.get_all_entries()
                unreconciled = [e for e in all_entries if e.reconciliation_status == "Unreconciled"]
                print(f"  Total entries: {len(all_entries)}")
                print(f"  Unreconciled entries: {len(unreconciled)}")
                
                # Show recent entries
                print("Recent unreconciled entries:")
                for entry in unreconciled[-3:]:  # Show last 3
                    print(f"  ID: {entry.id}, Date: {entry.date}, Description: {entry.description}, "
                          f"Amount: {entry.amount}")
            else:
                print("[WARNING] No entries to import")
                return False
                
        except Exception as e:
            print(f"[FAIL] Error importing entries: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n[SUCCESS] UI PDF import process completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to test UI PDF import process: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_pdf_import()
    if success:
        print("\n" + "=" * 50)
        print("CONCLUSION: UI PDF import should work correctly")
        print("If it's still failing in the application, the issue might be:")
        print("1. File dialog not returning correct path")
        print("2. Exception handling in the UI not showing detailed errors")
        print("3. Permission issues with the selected file")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("CONCLUSION: Issue identified in PDF import process")
        print("=" * 50)