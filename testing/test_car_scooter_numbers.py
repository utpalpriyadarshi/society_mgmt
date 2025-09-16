#!/usr/bin/env python3
"""
Test script to verify that car and scooter numbers are handled correctly
"""

import sys
import os
import sqlite3

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from gui.resident_form import ResidentForm

def setup_test_data():
    """Set up some test resident data with car and scooter numbers"""
    # Clear any existing test data
    conn = sqlite3.connect("society_management.db")
    cursor = conn.cursor()
    
    # Delete existing residents for clean test
    cursor.execute("DELETE FROM residents")
    
    # Insert test residents with car and scooter data
    test_residents = [
        ("A101", "John Doe", "Owner", "1234567890", "john@example.com", "2023-01-15", 
         2, 1, "P1", "AB1234CD\nXY9876ZW", "SG123456", 500.0, "Active", "Test resident 1"),
        ("B202", "Jane Smith", "Tenant", "0987654321", "jane@example.com", "2023-02-20", 
         1, 2, "P2", "PQ5678RS", "ST987654\nUV123456", 500.0, "Active", "Test resident 2"),
        ("C303", "Bob Johnson", "Owner", "1112223333", "bob@example.com", "2023-03-10", 
         0, 0, "", "", "", 500.0, "Inactive", "Test resident 3")
    ]
    
    for resident in test_residents:
        cursor.execute('''
            INSERT INTO residents (flat_no, name, resident_type, mobile_no, email, date_joining,
                                  cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', resident)
    
    conn.commit()
    conn.close()

def test_car_scooter_numbers():
    """Test that the resident data including car and scooter numbers is handled correctly"""
    app = QApplication(sys.argv)
    
    # Set up test data
    setup_test_data()
    
    # Create the resident form
    resident_form = ResidentForm()
    resident_form.load_residents()  # Load the test data
    
    # Check that we have the correct number of rows
    expected_rows = 3
    actual_rows = resident_form.table.rowCount()
    
    print(f"Expected rows: {expected_rows}")
    print(f"Actual rows: {actual_rows}")
    
    if actual_rows != expected_rows:
        print("FAIL: Row count is incorrect")
        return False
    
    # Check the data in the table
    test_data = [
        {
            "flat_no": "A101", 
            "name": "John Doe", 
            "car_nos": "AB1234CD, XY9876ZW", 
            "scooter_nos": "SG123456",
            "cars": "2",
            "scooters": "1"
        },
        {
            "flat_no": "B202", 
            "name": "Jane Smith", 
            "car_nos": "PQ5678RS", 
            "scooter_nos": "ST987654, UV123456",
            "cars": "1",
            "scooters": "2"
        },
        {
            "flat_no": "C303", 
            "name": "Bob Johnson", 
            "car_nos": "", 
            "scooter_nos": "",
            "cars": "0",
            "scooters": "0"
        }
    ]
    
    for row, expected in enumerate(test_data):
        # Check flat no (column 1)
        actual_flat_no = resident_form.table.item(row, 1).text()
        if actual_flat_no == expected["flat_no"]:
            print(f"PASS: Row {row} flat no is correct ({actual_flat_no})")
        else:
            print(f"FAIL: Row {row} flat no is incorrect. Expected: {expected['flat_no']}, Got: {actual_flat_no}")
            return False
        
        # Check name (column 2)
        actual_name = resident_form.table.item(row, 2).text()
        if actual_name == expected["name"]:
            print(f"PASS: Row {row} name is correct ({actual_name})")
        else:
            print(f"FAIL: Row {row} name is incorrect. Expected: {expected['name']}, Got: {actual_name}")
            return False
            
        # Check car numbers (column 5)
        actual_car_nos = resident_form.table.item(row, 5).text()
        if actual_car_nos == expected["car_nos"]:
            print(f"PASS: Row {row} car numbers is correct ({actual_car_nos})")
        else:
            print(f"FAIL: Row {row} car numbers is incorrect. Expected: {expected['car_nos']}, Got: {actual_car_nos}")
            return False
            
        # Check scooter numbers (column 6)
        actual_scooter_nos = resident_form.table.item(row, 6).text()
        if actual_scooter_nos == expected["scooter_nos"]:
            print(f"PASS: Row {row} scooter numbers is correct ({actual_scooter_nos})")
        else:
            print(f"FAIL: Row {row} scooter numbers is incorrect. Expected: {expected['scooter_nos']}, Got: {actual_scooter_nos}")
            return False
            
        # Check car count (column 7)
        actual_cars = resident_form.table.item(row, 7).text()
        if actual_cars == expected["cars"]:
            print(f"PASS: Row {row} cars count is correct ({actual_cars})")
        else:
            print(f"FAIL: Row {row} cars count is incorrect. Expected: {expected['cars']}, Got: {actual_cars}")
            return False
            
        # Check scooter count (column 8)
        actual_scooters = resident_form.table.item(row, 8).text()
        if actual_scooters == expected["scooters"]:
            print(f"PASS: Row {row} scooters count is correct ({actual_scooters})")
        else:
            print(f"FAIL: Row {row} scooters count is incorrect. Expected: {expected['scooters']}, Got: {actual_scooters}")
            return False
    
    print("All car and scooter numbers tests passed!")
    return True

if __name__ == "__main__":
    test_car_scooter_numbers()