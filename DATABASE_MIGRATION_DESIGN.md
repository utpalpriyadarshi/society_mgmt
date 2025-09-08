# Database Migration System Design

## Overview
This document describes the design of a database migration system for the Society Management System. The system will allow for controlled, versioned updates to the database schema as the application evolves.

## Current State Analysis
- Database version: 0 (no versioning currently implemented)
- Tables: residents, ledger, users, society, bank_statements, reconciliation_history, sessions
- Some tables have columns added outside of the original schema (car_numbers, scooter_numbers in residents; failed_login_attempts, locked_until in users)

## Migration System Architecture

### 1. Version Tracking
- Use SQLite's `PRAGMA user_version` to track the current database schema version
- Store migration scripts with version numbers
- Apply migrations sequentially from current version to target version

### 2. Migration Script Structure
- Each migration will be a Python function that takes a database connection as a parameter
- Migrations will be stored in `ai_agent_utils/migrations/` directory
- Migration files will be named with version numbers and descriptions:
  - `001_add_sessions_table.py`
  - `002_add_car_scooter_columns.py`
  - etc.

### 3. Migration Executor
- A script to apply pending migrations
- Will check current database version and apply all migrations with higher version numbers
- Will update `PRAGMA user_version` after each successful migration

### 4. Migration Safety
- Each migration will be wrapped in a transaction
- If a migration fails, the transaction will be rolled back
- Backup will be recommended before running migrations

## Migration Process

1. Check current database version using `PRAGMA user_version`
2. Identify pending migrations (files with version numbers higher than current version)
3. Apply each migration in order:
   - Start a transaction
   - Execute migration function
   - Update `PRAGMA user_version`
   - Commit transaction
4. Handle errors by rolling back transactions

## Initial Migrations

Based on the current database state, we need to create initial migrations:

1. Version 1: Create all tables as currently defined in database.py
2. Version 2: Add car_numbers and scooter_numbers columns to residents table
3. Version 3: Add failed_login_attempts and locked_until columns to users table
4. Version 4: Create sessions table

## Future Migrations

As new features are added, new migration files will be created:
- Add new columns
- Create new tables
- Modify existing columns
- Add indexes
- etc.

## Integration with Existing System

The Database class in database.py will be updated to:
1. Check database version on initialization
2. Apply pending migrations if needed
3. Continue with normal initialization

This approach ensures that the database schema is always up-to-date when the application starts.