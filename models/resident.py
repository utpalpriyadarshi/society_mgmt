# models/resident.py
import sqlite3
from datetime import datetime

class Resident:
    def __init__(self, resident_id, flat_no, name, resident_type, mobile_no, email, date_joining, 
                 cars, scooters, parking_slot, monthly_charges, status, remarks):
        self.id = resident_id
        self.flat_no = flat_no
        self.name = name
        self.resident_type = resident_type
        self.mobile_no = mobile_no
        self.email = email
        self.date_joining = date_joining
        self.cars = cars
        self.scooters = scooters
        self.parking_slot = parking_slot
        self.monthly_charges = monthly_charges
        self.status = status
        self.remarks = remarks

class ResidentManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def get_all_residents(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                   cars, scooters, parking_slot, monthly_charges, status, remarks
            FROM residents
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        residents = []
        for row in rows:
            resident = Resident(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[8], row[9], row[10], row[11], row[12]
            )
            residents.append(resident)
        
        return residents
    
    def get_resident_by_id(self, resident_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                   cars, scooters, parking_slot, monthly_charges, status, remarks
            FROM residents WHERE id = ?
        ''', (resident_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Resident(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[8], row[9], row[10], row[11], row[12]
            )
        return None
    
    def search_residents(self, search_term):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_pattern = f"%{search_term}%"
        cursor.execute('''
            SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                   cars, scooters, parking_slot, monthly_charges, status, remarks
            FROM residents
            WHERE flat_no LIKE ? OR name LIKE ? OR mobile_no LIKE ? OR email LIKE ?
        ''', (search_pattern, search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        residents = []
        for row in rows:
            resident = Resident(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[8], row[9], row[10], row[11], row[12]
            )
            residents.append(resident)
        
        return residents
    
    def add_resident(self, flat_no, name, resident_type, mobile_no, email, date_joining,
                     cars, scooters, parking_slot, monthly_charges, status, remarks):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Always set monthly charges to 500 (fixed)
            fixed_charges = 500.0
            
            cursor.execute('''
                INSERT INTO residents (flat_no, name, resident_type, mobile_no, email, date_joining,
                                      cars, scooters, parking_slot, monthly_charges, status, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (flat_no, name, resident_type, mobile_no, email, date_joining,
                  cars, scooters, parking_slot, fixed_charges, status, remarks))
            
            conn.commit()
            resident_id = cursor.lastrowid
            conn.close()
            return resident_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Duplicate flat_no
    
    def update_resident(self, resident_id, flat_no, name, resident_type, mobile_no, email, date_joining,
                        cars, scooters, parking_slot, monthly_charges, status, remarks):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Always set monthly charges to 500 (fixed)
            fixed_charges = 500.0
            
            cursor.execute('''
                UPDATE residents SET flat_no=?, name=?, resident_type=?, mobile_no=?, email=?, date_joining=?,
                                    cars=?, scooters=?, parking_slot=?, monthly_charges=?, status=?, remarks=?
                WHERE id=?
            ''', (flat_no, name, resident_type, mobile_no, email, date_joining,
                  cars, scooters, parking_slot, fixed_charges, status, remarks, resident_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Duplicate flat_no
    
    def delete_resident(self, resident_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM residents WHERE id=?', (resident_id,))
        
        conn.commit()
        conn.close()
        return True