# database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY,
            flat_no TEXT UNIQUE,
            name TEXT,
            resident_type TEXT,
            mobile_no TEXT,
            email TEXT,
            date_joining DATE,
            cars INTEGER,
            scooters INTEGER,
            parking_slot TEXT,
            car_numbers TEXT,
            scooter_numbers TEXT,
            monthly_charges REAL DEFAULT 500.0,
            status TEXT,
            remarks TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            date DATE,
            flat_no TEXT,
            transaction_type TEXT,
            category TEXT,
            description TEXT,
            debit REAL DEFAULT 0.0,
            credit REAL DEFAULT 0.0,
            balance REAL DEFAULT 0.0,
            payment_mode TEXT,
            entered_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reconciliation_status TEXT DEFAULT 'Unreconciled',
            FOREIGN KEY (flat_no) REFERENCES residents(flat_no)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            description TEXT,
            amount REAL,
            balance REAL,
            reference_number TEXT,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reconciliation_status TEXT DEFAULT 'Unreconciled',
            matched_ledger_id INTEGER,
            FOREIGN KEY (matched_ledger_id) REFERENCES ledger(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reconciliation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reconciliation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            period_start DATE,
            period_end DATE,
            matched_count INTEGER,
            unmatched_ledger_count INTEGER,
            unmatched_bank_count INTEGER,
            notes TEXT
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ledger_date ON ledger(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ledger_flat ON ledger(flat_no)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ledger_type ON ledger(transaction_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ledger_txn_id ON ledger(transaction_id)')
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP DEFAULT NULL
        )
        ''')
        
        # Create society table
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
        
        # Create system admin if not exists
        cursor.execute("SELECT id FROM users WHERE role = 'System Admin'")
        system_admin = cursor.fetchone()
        
        if not system_admin:
            # Create default system admin user
            from utils.security import hash_password
            default_password_hash = hash_password("systemadmin")
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("sysadmin", default_password_hash, "System Admin")
            )
        
        conn.commit()
        conn.close()