# models/accounting_period.py
import sqlite3
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class AccountingPeriod:
    def __init__(self, id, start_date, end_date, is_open, closed_at=None, closed_by=None):
        self.id = id
        self.start_date = start_date
        self.end_date = end_date
        self.is_open = is_open
        self.closed_at = closed_at
        self.closed_by = closed_by

class AccountingPeriodManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.init_period_table()
    
    def init_period_table(self):
        """Initialize the accounting_periods table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounting_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date DATE,
            end_date DATE,
            is_open INTEGER DEFAULT 1,  -- 1 for open, 0 for closed
            closed_at TIMESTAMP,
            closed_by TEXT
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_periods_dates ON accounting_periods(start_date, end_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_periods_open ON accounting_periods(is_open)')
        
        conn.commit()
        conn.close()
        
        # Initialize with default periods if empty
        self.initialize_default_periods()
    
    def initialize_default_periods(self):
        """Initialize default accounting periods if none exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM accounting_periods')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create initial periods for the current year
            current_year = datetime.now().year
            for month in range(1, 13):
                start_date = date(current_year, month, 1)
                if month == 12:
                    end_date = date(current_year, 12, 31)
                else:
                    end_date = date(current_year, month + 1, 1) - relativedelta(days=1)
                
                cursor.execute('''
                    INSERT INTO accounting_periods (start_date, end_date, is_open)
                    VALUES (?, ?, 1)
                ''', (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
    
    def get_current_period(self):
        """Get the current accounting period based on today's date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT id, start_date, end_date, is_open, closed_at, closed_by
            FROM accounting_periods
            WHERE start_date <= ? AND end_date >= ?
        ''', (today, today))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return AccountingPeriod(row[0], row[1], row[2], bool(row[3]), row[4], row[5])
        return None
    
    def is_period_open(self, date_str=None):
        """
        Check if the accounting period for a given date is open
        If no date is provided, checks the current date
        Returns (is_open: bool, period_info: dict)
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        period = self.get_current_period()
        if not period:
            return False, {"error": "No accounting period found for the given date"}
        
        return bool(period.is_open), {
            "period_id": period.id,
            "start_date": period.start_date,
            "end_date": period.end_date,
            "closed_at": period.closed_at,
            "closed_by": period.closed_by
        }
    
    def close_period(self, period_id, closed_by):
        """Close an accounting period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE accounting_periods 
            SET is_open = 0, closed_at = ?, closed_by = ?
            WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), closed_by, period_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_all_periods(self):
        """Get all accounting periods"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, start_date, end_date, is_open, closed_at, closed_by
            FROM accounting_periods
            ORDER BY start_date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        periods = []
        for row in rows:
            period = AccountingPeriod(row[0], row[1], row[2], bool(row[3]), row[4], row[5])
            periods.append(period)
        
        return periods