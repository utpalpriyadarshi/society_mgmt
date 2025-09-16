#!/usr/bin/env python3
"""
Test the improved error handling in the reconciliation tab
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_improved_error_handling():
    """Test the improved error handling"""
    print("Testing Improved Error Handling")
    print("=" * 40)
    
    try:
        # Import the reconciliation tab
        from gui.reconciliation_tab import ReconciliationTab
        
        # Create a mock reconciliation tab (without UI)
        class MockReconciliationTab(ReconciliationTab):
            def __init__(self):
                # Don't call parent __init__ to avoid UI creation
                pass
            
            def show_error_message(self, title, message):
                """Mock method to capture error messages"""
                print(f"[ERROR DIALOG] {title}: {message}")
        
        tab = MockReconciliationTab()
        
        # Test 1: Non-existent file
        print("Test 1: Non-existent file")
        tab.import_pdf_statement("non_existent_file.pdf")
        
        # Test 2: Directory instead of file
        print("\nTest 2: Directory instead of file")
        tab.import_pdf_statement(".")
        
        # Test 3: Empty PDF
        print("\nTest 3: Creating and testing empty PDF")
        try:
            import fitz
            # Create an empty PDF
            doc = fitz.open()
            page = doc.new_page()
            doc.save("empty_test.pdf")
            doc.close()
            
            tab.import_pdf_statement("empty_test.pdf")
            
            # Clean up
            os.remove("empty_test.pdf")
        except Exception as e:
            print(f"  Could not create test PDF: {e}")
        
        print("\n[SUCCESS] Error handling tests completed")
        
    except Exception as e:
        print(f"[ERROR] Failed to test error handling: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_error_handling()