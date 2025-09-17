# models/resident.py
from datetime import datetime
from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError
from utils.audit_logger import audit_logger
from utils.security import get_user_id
from models.vehicle import VehicleManager
from models.domestic_help import DomesticHelpManager


class Resident:
    def __init__(self, resident_id, flat_no, name, resident_type, mobile_no, email, date_joining, 
                 cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks,
                 profile_photo_path=None, vacancy_reason=None, expected_occupancy_date=None, 
                 last_maintenance_date=None, maintenance_person_name=None, maintenance_person_phone=None):
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
        self.profile_photo_path = profile_photo_path
        self.vacancy_reason = vacancy_reason
        self.expected_occupancy_date = expected_occupancy_date
        self.last_maintenance_date = last_maintenance_date
        self.maintenance_person_name = maintenance_person_name
        self.maintenance_person_phone = maintenance_person_phone


class ResidentManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.domestic_help_manager = DomesticHelpManager(db_path)
    
    def get_all_residents(self):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks,
                           profile_photo_path, vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                           maintenance_person_name, maintenance_person_phone
                    FROM residents
                ''')
                
                rows = cursor.fetchall()
                
                residents = []
                for row in rows:
                    resident = Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                        row[15], row[16], row[17], row[18], row[19], row[20]
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
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks,
                           profile_photo_path, vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                           maintenance_person_name, maintenance_person_phone
                    FROM residents WHERE id = ?
                ''', (resident_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                        row[15], row[16], row[17], row[18], row[19], row[20]
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
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks,
                           profile_photo_path, vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                           maintenance_person_name, maintenance_person_phone
                    FROM residents
                    WHERE flat_no LIKE ? OR name LIKE ? OR mobile_no LIKE ? OR email LIKE ?
                ''', (search_pattern, search_pattern, search_pattern, search_pattern))
                
                rows = cursor.fetchall()
                
                residents = []
                for row in rows:
                    resident = Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                        row[15], row[16], row[17], row[18], row[19], row[20]
                    )
                    residents.append(resident)
                
                return residents
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to search residents", original_error=e)
    
    def advanced_search_residents(self, filters=None, sort_by=None, sort_order="ASC"):
        """
        Advanced search for residents with multiple filter options and sorting.
        
        Args:
            filters (dict): Dictionary of filter criteria
            sort_by (str): Column to sort by
            sort_order (str): Sort order ("ASC" or "DESC")
        
        Returns:
            list: List of Resident objects matching the criteria
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Base query
                query = '''
                    SELECT id, flat_no, name, resident_type, mobile_no, email, date_joining,
                           cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks,
                           profile_photo_path, vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                           maintenance_person_name, maintenance_person_phone
                    FROM residents
                '''
                
                # Build WHERE clause based on filters
                where_conditions = []
                params = []
                
                if filters:
                    # Text search
                    if filters.get('search_term'):
                        search_pattern = f"%{filters['search_term']}%"
                        where_conditions.append('''
                            (flat_no LIKE ? OR name LIKE ? OR mobile_no LIKE ? OR email LIKE ?)
                        ''')
                        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
                    
                    # Resident type filter
                    if filters.get('resident_type'):
                        where_conditions.append('resident_type = ?')
                        params.append(filters['resident_type'])
                    
                    # Status filter
                    if filters.get('status'):
                        where_conditions.append('status = ?')
                        params.append(filters['status'])
                    
                    # Vehicle filters
                    if filters.get('has_cars') is True:
                        where_conditions.append('cars > 0')
                    elif filters.get('has_cars') is False:
                        where_conditions.append('cars = 0')
                    
                    if filters.get('has_scooters') is True:
                        where_conditions.append('scooters > 0')
                    elif filters.get('has_scooters') is False:
                        where_conditions.append('scooters = 0')
                    
                    # Vacant flat filters
                    if filters.get('is_vacant') is True:
                        where_conditions.append('resident_type = "Vacant"')
                    elif filters.get('is_vacant') is False:
                        where_conditions.append('resident_type != "Vacant"')
                    
                    # Vacancy reason filter
                    if filters.get('vacancy_reason'):
                        where_conditions.append('vacancy_reason = ?')
                        params.append(filters['vacancy_reason'])
                    
                    # Date range filters
                    if filters.get('date_from'):
                        where_conditions.append('date_joining >= ?')
                        params.append(filters['date_from'])
                    
                    if filters.get('date_to'):
                        where_conditions.append('date_joining <= ?')
                        params.append(filters['date_to'])
                
                # Add WHERE clause if we have conditions
                if where_conditions:
                    query += ' WHERE ' + ' AND '.join(where_conditions)
                
                # Add ORDER BY clause
                if sort_by:
                    # Validate sort_by to prevent SQL injection
                    valid_sort_columns = [
                        'id', 'flat_no', 'name', 'resident_type', 'mobile_no', 'email', 'date_joining',
                        'cars', 'scooters', 'monthly_charges', 'status'
                    ]
                    if sort_by in valid_sort_columns:
                        # Ensure sort_order is either ASC or DESC
                        order = "ASC" if sort_order.upper() != "DESC" else "DESC"
                        query += f' ORDER BY {sort_by} {order}'
                
                # Execute query
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                residents = []
                for row in rows:
                    resident = Resident(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                        row[15], row[16], row[17], row[18], row[19], row[20]
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
                     cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks, 
                     current_user=None, vacancy_reason=None, expected_occupancy_date=None, 
                     last_maintenance_date=None, maintenance_person_name=None, maintenance_person_phone=None):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Always set monthly charges to 500 (fixed)
                fixed_charges = 500.0
                
                cursor.execute('''
                    INSERT INTO residents (flat_no, name, resident_type, mobile_no, email, date_joining,
                                          cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks,
                                          vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                                          maintenance_person_name, maintenance_person_phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (flat_no, name, resident_type, mobile_no, email, date_joining,
                      cars, scooters, parking_slot, car_numbers, scooter_numbers, fixed_charges, status, remarks,
                      vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                      maintenance_person_name, maintenance_person_phone))
                
                conn.commit()
                resident_id = cursor.lastrowid
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                new_values = {
                    'flat_no': flat_no,
                    'name': name,
                    'resident_type': resident_type,
                    'mobile_no': mobile_no,
                    'email': email,
                    'date_joining': date_joining,
                    'cars': cars,
                    'scooters': scooters,
                    'parking_slot': parking_slot,
                    'car_numbers': car_numbers,
                    'scooter_numbers': scooter_numbers,
                    'monthly_charges': fixed_charges,
                    'status': status,
                    'remarks': remarks,
                    'vacancy_reason': vacancy_reason,
                    'expected_occupancy_date': expected_occupancy_date,
                    'last_maintenance_date': last_maintenance_date,
                    'maintenance_person_name': maintenance_person_name,
                    'maintenance_person_phone': maintenance_person_phone
                }
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="CREATE_RESIDENT",
                    table_name="residents",
                    record_id=resident_id,
                    new_values=new_values
                )
                
                return resident_id
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to add resident", original_error=e)
    
    def update_resident(self, resident_id, flat_no, name, resident_type, mobile_no, email, date_joining,
                        cars, scooters, parking_slot, car_numbers, scooter_numbers, monthly_charges, status, remarks, 
                        current_user=None, vacancy_reason=None, expected_occupancy_date=None, 
                        last_maintenance_date=None, maintenance_person_name=None, maintenance_person_phone=None):
        try:
            # First get the old values for logging
            old_resident = self.get_resident_by_id(resident_id)
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Always set monthly charges to 500 (fixed)
                fixed_charges = 500.0
                
                cursor.execute('''
                    UPDATE residents SET flat_no=?, name=?, resident_type=?, mobile_no=?, email=?, date_joining=?,
                                        cars=?, scooters=?, parking_slot=?, car_numbers=?, scooter_numbers=?, monthly_charges=?, status=?, remarks=?,
                                        vacancy_reason=?, expected_occupancy_date=?, last_maintenance_date=?, 
                                        maintenance_person_name=?, maintenance_person_phone=?
                    WHERE id=?
                ''', (flat_no, name, resident_type, mobile_no, email, date_joining,
                      cars, scooters, parking_slot, car_numbers, scooter_numbers, fixed_charges, status, remarks,
                      vacancy_reason, expected_occupancy_date, last_maintenance_date, 
                      maintenance_person_name, maintenance_person_phone, resident_id))
                
                conn.commit()
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                old_values = {
                    'flat_no': old_resident.flat_no,
                    'name': old_resident.name,
                    'resident_type': old_resident.resident_type,
                    'mobile_no': old_resident.mobile_no,
                    'email': old_resident.email,
                    'date_joining': old_resident.date_joining,
                    'cars': old_resident.cars,
                    'scooters': old_resident.scooters,
                    'parking_slot': old_resident.parking_slot,
                    'car_numbers': old_resident.car_numbers,
                    'scooter_numbers': old_resident.scooter_numbers,
                    'monthly_charges': old_resident.monthly_charges,
                    'status': old_resident.status,
                    'remarks': old_resident.remarks,
                    'vacancy_reason': old_resident.vacancy_reason,
                    'expected_occupancy_date': old_resident.expected_occupancy_date,
                    'last_maintenance_date': old_resident.last_maintenance_date,
                    'maintenance_person_name': old_resident.maintenance_person_name,
                    'maintenance_person_phone': old_resident.maintenance_person_phone
                } if old_resident else None
                
                new_values = {
                    'flat_no': flat_no,
                    'name': name,
                    'resident_type': resident_type,
                    'mobile_no': mobile_no,
                    'email': email,
                    'date_joining': date_joining,
                    'cars': cars,
                    'scooters': scooters,
                    'parking_slot': parking_slot,
                    'car_numbers': car_numbers,
                    'scooter_numbers': scooter_numbers,
                    'monthly_charges': fixed_charges,
                    'status': status,
                    'remarks': remarks,
                    'vacancy_reason': vacancy_reason,
                    'expected_occupancy_date': expected_occupancy_date,
                    'last_maintenance_date': last_maintenance_date,
                    'maintenance_person_name': maintenance_person_name,
                    'maintenance_person_phone': maintenance_person_phone
                }
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="UPDATE_RESIDENT",
                    table_name="residents",
                    record_id=resident_id,
                    old_values=old_values,
                    new_values=new_values
                )
                
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to update resident", original_error=e)
    
    def delete_resident(self, resident_id, current_user=None):
        try:
            # First get the resident details for logging
            resident = self.get_resident_by_id(resident_id)
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM residents WHERE id=?', (resident_id,))
                
                conn.commit()
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                old_values = {
                    'flat_no': resident.flat_no,
                    'name': resident.name,
                    'resident_type': resident.resident_type,
                    'mobile_no': resident.mobile_no,
                    'email': resident.email,
                    'date_joining': resident.date_joining,
                    'cars': resident.cars,
                    'scooters': resident.scooters,
                    'parking_slot': resident.parking_slot,
                    'car_numbers': resident.car_numbers,
                    'scooter_numbers': resident.scooter_numbers,
                    'monthly_charges': resident.monthly_charges,
                    'status': resident.status,
                    'remarks': resident.remarks,
                    'vacancy_reason': resident.vacancy_reason,
                    'expected_occupancy_date': resident.expected_occupancy_date,
                    'last_maintenance_date': resident.last_maintenance_date,
                    'maintenance_person_name': resident.maintenance_person_name,
                    'maintenance_person_phone': resident.maintenance_person_phone
                } if resident else None
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="DELETE_RESIDENT",
                    table_name="residents",
                    record_id=resident_id,
                    old_values=old_values
                )
                
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to delete resident", original_error=e)
    
    def get_domestic_help_by_resident(self, resident_id):
        """Get all domestic help for a specific resident."""
        return self.domestic_help_manager.get_domestic_help_by_resident(resident_id)