# models/vehicle.py
"""
Vehicle data model and manager for the Society Management System.
"""

from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError
from utils.audit_logger import audit_logger
from utils.security import get_user_id


class Vehicle:
    def __init__(self, vehicle_id, resident_id, vehicle_type, registration_number=None, 
                 make=None, model=None, color=None, parking_slot=None, status="Active"):
        self.id = vehicle_id
        self.resident_id = resident_id
        self.vehicle_type = vehicle_type
        self.registration_number = registration_number
        self.make = make
        self.model = model
        self.color = color
        self.parking_slot = parking_slot
        self.status = status


class VehicleManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def get_vehicles_by_resident(self, resident_id):
        """Get all vehicles for a specific resident."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, resident_id, vehicle_type, registration_number, make, model, color, parking_slot, status
                    FROM vehicles WHERE resident_id = ? ORDER BY vehicle_type, registration_number
                ''', (resident_id,))
                
                rows = cursor.fetchall()
                
                vehicles = []
                for row in rows:
                    vehicle = Vehicle(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                    )
                    vehicles.append(vehicle)
                
                return vehicles
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve vehicles", original_error=e)
    
    def add_vehicle(self, resident_id, vehicle_type, registration_number=None, 
                   make=None, model=None, color=None, parking_slot=None, status="Active", current_user=None):
        """Add a new vehicle for a resident."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO vehicles (resident_id, vehicle_type, registration_number, make, model, color, parking_slot, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (resident_id, vehicle_type, registration_number, make, model, color, parking_slot, status))
                
                conn.commit()
                vehicle_id = cursor.lastrowid
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                new_values = {
                    'resident_id': resident_id,
                    'vehicle_type': vehicle_type,
                    'registration_number': registration_number,
                    'make': make,
                    'model': model,
                    'color': color,
                    'parking_slot': parking_slot,
                    'status': status
                }
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="CREATE_VEHICLE",
                    table_name="vehicles",
                    record_id=vehicle_id,
                    new_values=new_values
                )
                
                return vehicle_id
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to add vehicle", original_error=e)
    
    def update_vehicle(self, vehicle_id, vehicle_type, registration_number=None, 
                      make=None, model=None, color=None, parking_slot=None, status="Active", current_user=None):
        """Update an existing vehicle."""
        try:
            # First get the old values for logging
            old_vehicle = self.get_vehicle_by_id(vehicle_id)
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE vehicles 
                    SET vehicle_type=?, registration_number=?, make=?, model=?, color=?, parking_slot=?, status=?
                    WHERE id=?
                ''', (vehicle_type, registration_number, make, model, color, parking_slot, status, vehicle_id))
                
                conn.commit()
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                old_values = {
                    'vehicle_type': old_vehicle.vehicle_type,
                    'registration_number': old_vehicle.registration_number,
                    'make': old_vehicle.make,
                    'model': old_vehicle.model,
                    'color': old_vehicle.color,
                    'parking_slot': old_vehicle.parking_slot,
                    'status': old_vehicle.status
                } if old_vehicle else None
                
                new_values = {
                    'vehicle_type': vehicle_type,
                    'registration_number': registration_number,
                    'make': make,
                    'model': model,
                    'color': color,
                    'parking_slot': parking_slot,
                    'status': status
                }
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="UPDATE_VEHICLE",
                    table_name="vehicles",
                    record_id=vehicle_id,
                    old_values=old_values,
                    new_values=new_values
                )
                
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to update vehicle", original_error=e)
    
    def get_vehicle_by_id(self, vehicle_id):
        """Get a specific vehicle by ID."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, resident_id, vehicle_type, registration_number, make, model, color, parking_slot, status
                    FROM vehicles WHERE id = ?
                ''', (vehicle_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return Vehicle(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                    )
                return None
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve vehicle", original_error=e)
    
    def delete_vehicle(self, vehicle_id, current_user=None):
        """Delete a vehicle."""
        try:
            # First get the vehicle details for logging
            vehicle = self.get_vehicle_by_id(vehicle_id)
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM vehicles WHERE id=?', (vehicle_id,))
                
                conn.commit()
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                old_values = {
                    'resident_id': vehicle.resident_id,
                    'vehicle_type': vehicle.vehicle_type,
                    'registration_number': vehicle.registration_number,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'color': vehicle.color,
                    'parking_slot': vehicle.parking_slot,
                    'status': vehicle.status
                } if vehicle else None
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="DELETE_VEHICLE",
                    table_name="vehicles",
                    record_id=vehicle_id,
                    old_values=old_values
                )
                
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to delete vehicle", original_error=e)
    
    def get_vehicle_count_by_resident(self, resident_id):
        """Get vehicle counts by type for a specific resident."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT vehicle_type, COUNT(*) as count
                    FROM vehicles 
                    WHERE resident_id = ? AND status = 'Active'
                    GROUP BY vehicle_type
                ''', (resident_id,))
                
                rows = cursor.fetchall()
                
                # Return as a dictionary
                counts = {}
                for row in rows:
                    counts[row[0]] = row[1]
                
                return counts
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve vehicle counts", original_error=e)