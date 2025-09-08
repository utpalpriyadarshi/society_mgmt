#!/usr/bin/env python3
"""
Script to reset database migrations for the Society Management System.
"""

import sqlite3
import os
import sys
import argparse

def reset_database_version(db_path="society_management.db"):
    """Reset the database version to 0"""
    print(f"Resetting database version for {db_path}...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version = 0")
            conn.commit()
            print("Database version reset to 0")
    except Exception as e:
        print(f"Error resetting database version: {e}")
        return False
        
    return True

def show_current_version(db_path="society_management.db"):
    """Show the current database version"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            print(f"Current database version: {version}")
            return version
    except Exception as e:
        print(f"Error checking database version: {e}")
        return None

def drop_all_tables(db_path="society_management.db"):
    """Drop all tables from the database (optional clean slate)"""
    print("Dropping all tables...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Drop each table
            for table in tables:
                table_name = table[0]
                # Skip sqlite_sequence table as it's managed by SQLite
                if table_name != 'sqlite_sequence':
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    print(f"  Dropped table: {table_name}")
            
            conn.commit()
            print("All tables dropped successfully")
    except Exception as e:
        print(f"Error dropping tables: {e}")
        return False
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Reset database migrations for the Society Management System")
    parser.add_argument("--db-path", default="society_management.db", help="Path to the database file")
    parser.add_argument("--drop-tables", action="store_true", help="Drop all tables (clean slate)")
    parser.add_argument("--show-version", action="store_true", help="Show current database version only")
    
    args = parser.parse_args()
    
    print("Database Migration Reset Tool")
    print("=" * 30)
    
    # Show current status
    print("\nCurrent status:")
    version = show_current_version(args.db_path)
    if version is None:
        return
    
    if args.show_version:
        return
    
    if args.drop_tables:
        print("\nResetting migrations and dropping all tables...")
        print("WARNING: This will delete all data in the database!")
        if drop_all_tables(args.db_path) and reset_database_version(args.db_path):
            print("Migrations reset and tables dropped successfully!")
            show_current_version(args.db_path)
    else:
        print("\nResetting migrations only...")
        if reset_database_version(args.db_path):
            print("Migrations reset successfully!")
            show_current_version(args.db_path)

if __name__ == "__main__":
    main()