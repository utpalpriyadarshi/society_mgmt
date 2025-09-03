# models/society.py
import sqlite3
import json

class Society:
    def __init__(self, society_id, name, address, phone, email, bank_details):
        self.id = society_id
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.bank_details = bank_details

class SocietyManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.init_table()
    
    def init_table(self):
        """Initialize the society table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS society (
                id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                bank_details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_society_info(self):
        """Retrieve society information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, address, phone, email, bank_details
            FROM society
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Society(
                row[0], row[1], row[2], row[3], row[4], 
                json.loads(row[5]) if row[5] else {}
            )
        return None
    
    def save_society_info(self, name, address, phone, email, bank_details):
        """Save or update society information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('SELECT id FROM society')
        exists = cursor.fetchone()
        
        if exists:
            # Update existing record
            cursor.execute('''
                UPDATE society 
                SET name=?, address=?, phone=?, email=?, bank_details=?
            ''', (name, address, phone, email, json.dumps(bank_details)))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO society (name, address, phone, email, bank_details)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, address, phone, email, json.dumps(bank_details)))
        
        conn.commit()
        conn.close()
        return True