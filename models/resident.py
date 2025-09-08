# models/resident.py
from datetime import datetime
from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError

class Resident:
    def __init__(self, resident_id, flat_no, name, resident_type, mobile_no, email, date_joining, 
                 cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks):
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
        self.car_numbers = car_numbers
        self.scooter_numbers = scooter_numbers
        self.monthly_charges = monthly_charges
        self.status = status
        self.remarks = remarks

class ResidentManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def get_all_residents(self):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks
                    FROM residents
                ''')
                
                rows = cursor.fetchall()
                
                residents = []
                for row in rows:
                    resident = Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]
                    )
                    residents.append(resident)
                
                return residents
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve residents", original_error=e)
    
    def get_resident_by_id(self, resident_id):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks
                    FROM residents WHERE id = ?
                ''', (resident_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]
                    )
                return None
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve resident", original_error=e)
    
    def search_residents(self, search_term):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{search_term}%"
                cursor.execute('''
                    SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks
                    FROM residents
                    WHERE flat_no LIKE ? OR name LIKE ? OR mobile_no LIKE ? OR email LIKE ?
                ''', (search_pattern, search_pattern, search_pattern, search_pattern))
                
                rows = cursor.fetchall()
                
                residents = []
                for row in rows:
                    resident = Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]
                    )
                    residents.append(resident)
                
                return residents
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to search residents", original_error=e)
    
    def add_resident(self, flat_no, name, resident_type, mobile_no, email, date_joining,
                     cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Always set monthly charges to 500 (fixed)
                fixed_charges = 500.0
                
                cursor.execute('''
                    INSERT INTO residents (flat_no, name, resident_type, mobile_no, email, date_joining,
                                          cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (flat_no, name, resident_type, mobile_no, email, date_joining,
                      cars, scooters, parking_slot, car_numbers, scooter_numbers, fixed_charges, status, remarks))
                
                conn.commit()
                resident_id = cursor.lastrowid
                return resident_id
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to add resident", original_error=e)
    
    def update_resident(self, resident_id, flat_no, name, resident_type, mobile_no, email, date_joining,
                        cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Always set monthly charges to 500 (fixed)
                fixed_charges = 500.0
                
                cursor.execute('''
                    UPDATE residents SET flat_no=?, name=?, resident_type=?, mobile_no=?, email=?, date_joining=?,
                                        cars=?, scooters=?, parking_slot=?, car_numbers=?, scooter_numbers=?, monthly_charges=?, status=?, remarks=?
                    WHERE id=?
                ''', (flat_no, name, resident_type, mobile_no, email, date_joining,
                      cars, scooters, parking_slot, car_numbers, scooter_numbers, fixed_charges, status, remarks, resident_id))
                
                conn.commit()
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to update resident", original_error=e)
    
    def delete_resident(self, resident_id):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM residents WHERE id=?', (resident_id,))
                
                conn.commit()
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to delete resident", original_error=e)