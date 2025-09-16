#!/usr/bin/env python3
"""
Test script to verify that search functionality works with the updated resident table
"""

import sys
import os
import sqlite3

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from gui.resident_form import ResidentForm

def setup_test_data():
    """Set up some test resident data"""
    # Clear any existing test data
    conn = sqlite3.connect("society_management.db")
    cursor = conn.cursor()
    
    # Delete existing residents for clean test
    cursor.execute("DELETE FROM residents")
    
    # Insert test residents
    test_residents = [
        ("A101", "John Doe", "Owner", "1234567890", "john@example.com", "2023-01-15", 2, 1, "P1", 500.0, "Active", "Test resident 1"),
        ("B202", "Jane Smith", "Tenant", "0987654321", "jane@example.com", "2023-02-20", 1, 2, "P2", 500.0, "Active", "Test resident 2"),
        ("C303", "Bob Johnson", "Owner", "1112223333", "bob@example.com", "2023-03-10", 0, 0, "", 500.0, "Inactive", "Test resident 3")
    ]
    
    for resident in test_residents:
        cursor.execute('''
            INSERT INTO residents (flat_no, name, resident_type, mobile_no, email, date_joining,
                                  cars, scooters, parking_slot, monthly_charges, status, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', resident)
    
    conn.commit()
    conn.close()

def test_search_functionality():
    """Test that the search functionality works correctly with the updated table"""
    app = QApplication(sys.argv)
    
    # Set up test data
    setup_test_data()
    
    # Create the resident form
    resident_form = ResidentForm()
    resident_form.load_residents()  # Load the test data
    
    # Test search by flat number
    resident_form.search_input.setText("A101")
    # The filter_residents method should be called automatically by the signal
    
    # Check that we have the correct number of rows after search
    expected_rows = 1
    actual_rows = resident_form.table.rowCount()
    
    print(f"Search by flat no 'A101' - Expected rows: {expected_rows}")
    print(f"Search by flat no 'A101' - Actual rows: {actual_rows}")
    
    if actual_rows == expected_rows:
        print("PASS: Search by flat no works correctly")
    else:
        print("FAIL: Search by flat no doesn't work correctly")
        return False
    
    # Test search by name
    resident_form.search_input.setText("Jane")
    # The filter_residents method should be called automatically by the signal
    
    # Check that we have the correct number of rows after search
    expected_rows = 1
    actual_rows = resident_form.table.rowCount()
    
    print(f"Search by name 'Jane' - Expected rows: {expected_rows}")
    print(f"Search by name 'Jane' - Actual rows: {actual_rows}")
    
    if actual_rows == expected_rows:
        print("PASS: Search by name works correctly")
    else:
        print("FAIL: Search by name doesn't work correctly")
        return False
    
    # Test search by phone number
    resident_form.search_input.setText("1234567890")
    # The filter_residents method should be called automatically by the signal
    
    # Check that we have the correct number of rows after search
    expected_rows = 1
    actual_rows = resident_form.table.rowCount()
    
    print(f"Search by phone '1234567890' - Expected rows: {expected_rows}")
    print(f"Search by phone '1234567890' - Actual rows: {actual_rows}")
    
    if actual_rows == expected_rows:
        print("PASS: Search by phone works correctly")
    else:
        print("FAIL: Search by phone doesn't work correctly")
        return False
    
    # Test search by email
    resident_form.search_input.setText("example.com")
    # The filter_residents method should be called automatically by the signal
    
    # Check that we have the correct number of rows after search (should find all 3)
    expected_rows = 3
    actual_rows = resident_form.table.rowCount()
    
    print(f"Search by email 'example.com' - Expected rows: {expected_rows}")
    print(f"Search by email 'example.com' - Actual rows: {actual_rows}")
    
    if actual_rows == expected_rows:
        print("PASS: Search by email works correctly")
    else:
        print("FAIL: Search by email doesn't work correctly")
        return False
    
    print("All search functionality tests passed!")
    return True

if __name__ == "__main__":
    test_search_functionality()