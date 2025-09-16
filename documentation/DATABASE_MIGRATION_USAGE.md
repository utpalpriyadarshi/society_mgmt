# Database Migration System

## Overview
The Society Management System now includes a database migration system that allows for controlled, versioned updates to the database schema as the application evolves.

## Migration Files
Migration files are stored in the `ai_agent_utils/migrations/` directory. Each migration file is named with a version number and description:
- `001_initial_schema.py` - Creates the initial database schema
- `002_add_sessions_table.py` - Adds the sessions table for user session management
- `003_add_resident_vehicle_columns.py` - Adds car_numbers and scooter_numbers columns to residents table
- `004_add_user_security_columns.py` - Adds failed_login_attempts and locked_until columns to users table
- `005_add_parking_columns_to_residents.py` - Adds parking_slot column to residents table

## Applying Migrations
Migrations can be applied using the `apply_migrations.py` script in the `ai_agent_utils` directory:

```bash
# Apply migrations with interactive prompt
python ai_agent_utils/apply_migrations.py

# Apply migrations automatically without prompting
python ai_agent_utils/apply_migrations.py --auto-approve

# Apply migrations with custom database path
python ai_agent_utils/apply_migrations.py --auto-approve --db-path /path/to/database.db
```

## Creating New Migrations
To create a new migration:

1. Create a new file in `ai_agent_utils/migrations/` with the next version number and a descriptive name:
   - `006_description_of_changes.py`

2. The migration file should contain a `migrate(conn)` function that takes a database connection as a parameter:
   ```python
   import sqlite3
   
   def migrate(conn):
       cursor = conn.cursor()
       # Add your schema changes here
       cursor.execute("ALTER TABLE table_name ADD COLUMN new_column TEXT")
   ```

3. The migration will be automatically applied when the database is initialized or when the apply_migrations script is run.

## How It Works
1. The system uses SQLite's `PRAGMA user_version` to track the current database schema version
2. When the Database class is initialized, it automatically applies any pending migrations
3. Each migration is applied in a transaction to ensure atomicity
4. If a migration fails, the transaction is rolled back and no changes are made to the database

## Best Practices
1. Always test migrations on a copy of the database before applying to production
2. Keep migrations simple and focused on a single change
3. Backup the database before applying migrations
4. Write migrations that are idempotent (can be run multiple times without harm)

## Troubleshooting
If you encounter issues with migrations:
1. Check that all migration files have the correct import statements
2. Verify that the database file path is correct
3. Check that the database is not locked by another process
4. Review the error message for specific details about what went wrong