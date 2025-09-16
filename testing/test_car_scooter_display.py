#!/usr/bin/env python3
"""
Test script to verify that car and scooter columns are displayed in resident management
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from gui.resident_form import ResidentForm
from models.resident import ResidentManager

def test_resident_table_columns():
    """Test that the resident table has the correct columns including car and scooter"""
    app = QApplication(sys.argv)
    
    # Create the resident form
    resident_form = ResidentForm()
    
    # Check the number of columns
    expected_columns = 7  # ID, Flat No, Name, Phone No, Email, Cars, Scooters
    actual_columns = resident_form.table.columnCount()
    
    print(f"Expected columns: {expected_columns}")
    print(f"Actual columns: {actual_columns}")
    
    if actual_columns == expected_columns:
        print("PASS: Column count is correct")
    else:
        print("FAIL: Column count is incorrect")
        return False
    
    # Check the column headers
    expected_headers = ["ID", "Flat No", "Name", "Phone No", "Email", "Cars", "Scooters"]
    for i, expected_header in enumerate(expected_headers):
        actual_header = resident_form.table.horizontalHeaderItem(i).text()
        if actual_header == expected_header:
            print(f"PASS: Column {i} header is correct ({actual_header})")
        else:
            print(f"FAIL: Column {i} header is incorrect. Expected: {expected_header}, Got: {actual_header}")
            return False
    
    # Check that ID column is hidden
    if resident_form.table.isColumnHidden(0):
        print("PASS: ID column is hidden")
    else:
        print("FAIL: ID column is not hidden")
        return False
    
    print("All tests passed!")
    return True

if __name__ == "__main__":
    test_resident_table_columns()