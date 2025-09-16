# Data Migration Testing Procedure

## Overview
This document describes the procedure for testing data migrations in the Society Management System. Data migrations are used to transform existing data when the database schema changes.

## Types of Data Migrations

1. **Schema-Only Migrations**: Changes to database structure without data transformation
2. **Data Transformation Migrations**: Changes that require modifying existing data
3. **Data Population Migrations**: Adding new data to support new features

## Testing Procedure

### 1. Pre-Migration Testing

#### 1.1. Backup Verification
- Create a backup of the database before testing
- Verify backup integrity using the verification procedure

#### 1.2. Data Sampling
- Extract a sample of data from each table that will be affected by the migration
- Document the current state of the data
- Include boundary cases and special values

#### 1.3. Environment Setup
- Use a test database that mirrors production data
- Ensure the test environment matches the production environment as closely as possible

### 2. Migration Testing

#### 2.1. Schema Migration Testing
- Apply schema-only migrations to verify they don't corrupt existing data
- Check that all existing data is still accessible
- Verify that new columns/tables exist and have correct properties

#### 2.2. Data Transformation Testing
- For migrations that transform data:
  - Create test data that covers all transformation cases
  - Apply the migration
  - Verify that data was transformed correctly
  - Check for data loss or corruption

#### 2.3. Data Population Testing
- For migrations that add new data:
  - Verify that the correct data was added
  - Check that the data is consistent with business rules
  - Ensure no duplicate or conflicting data was created

### 3. Post-Migration Testing

#### 3.1. Functional Testing
- Test all application features that interact with migrated data
- Verify that existing functionality still works correctly
- Check that new functionality (if any) works as expected

#### 3.2. Data Integrity Testing
- Run consistency checks on the migrated data
- Verify referential integrity between tables
- Check for any null values in non-nullable columns

#### 3.3. Performance Testing
- Test query performance on migrated data
- Check that indexes are working correctly
- Verify that the migration didn't introduce performance issues

### 4. Rollback Testing

#### 4.1. Migration Reversal
- Test that migrations can be reversed if needed
- Verify that data is restored to its original state
- Check that the application still functions correctly

### 5. Edge Case Testing

#### 5.1. Large Data Sets
- Test migrations with large volumes of data
- Check that the migration completes in a reasonable time
- Verify memory usage is within acceptable limits

#### 5.2. Invalid Data
- Test how migrations handle invalid or corrupted data
- Verify that appropriate error messages are displayed
- Check that valid data is not affected by invalid data

## Test Data Creation

### Sample Data Templates
Create templates for generating test data:

1. **Residents Table**
   - Valid resident records with all fields populated
   - Residents with minimal information
   - Residents with special characters in names
   - Residents with multiple vehicles

2. **Ledger Table**
   - Various transaction types (payments, expenses)
   - Transactions with different dates
   - Transactions with different amounts (including zero and negative values)

3. **Users Table**
   - Users with different roles
   - Users with various password formats
   - Users with special characters in usernames

## Test Scripts

### Data Validation Script
Create a script to validate data integrity after migration:

```python
# ai_agent_utils/validate_migration.py
import sqlite3

def validate_residents_data(conn):
    """Validate residents data after migration"""
    cursor = conn.cursor()
    
    # Check that all residents have valid flat numbers
    cursor.execute("SELECT COUNT(*) FROM residents WHERE flat_no IS NULL OR flat_no = ''")
    null_flats = cursor.fetchone()[0]
    assert null_flats == 0, f"Found {null_flats} residents with null or empty flat numbers"
    
    # Add more validation checks as needed
    print("Residents data validation passed")

def validate_ledger_data(conn):
    """Validate ledger data after migration"""
    cursor = conn.cursor()
    
    # Check that all transactions have valid dates
    cursor.execute("SELECT COUNT(*) FROM ledger WHERE date IS NULL")
    null_dates = cursor.fetchone()[0]
    assert null_dates == 0, f"Found {null_dates} transactions with null dates"
    
    # Add more validation checks as needed
    print("Ledger data validation passed")

def validate_users_data(conn):
    """Validate users data after migration"""
    cursor = conn.cursor()
    
    # Check that all users have valid usernames
    cursor.execute("SELECT COUNT(*) FROM users WHERE username IS NULL OR username = ''")
    null_usernames = cursor.fetchone()[0]
    assert null_usernames == 0, f"Found {null_usernames} users with null or empty usernames"
    
    # Add more validation checks as needed
    print("Users data validation passed")

def validate_all_data(db_path):
    """Run all data validation checks"""
    conn = sqlite3.connect(db_path)
    try:
        validate_residents_data(conn)
        validate_ledger_data(conn)
        validate_users_data(conn)
        print("All data validation checks passed")
    finally:
        conn.close()
```

## Test Execution Procedure

### 1. Prepare Test Environment
```bash
# Create test database
python -c "import sqlite3; conn = sqlite3.connect('test_data_migration.db'); conn.close()"

# Apply current migrations
python ai_agent_utils/apply_migrations.py --auto-approve --db-path test_data_migration.db
```

### 2. Populate Test Data
```bash
# Run script to populate test data
python ai_agent_utils/populate_test_data.py --db-path test_data_migration.db
```

### 3. Create New Migration
```bash
# Create new migration file
cp ai_agent_utils/migrations/006_template.py ai_agent_utils/migrations/007_data_migration_test.py
# Edit the migration file to implement the data transformation
```

### 4. Apply Migration
```bash
# Apply the new migration
python ai_agent_utils/apply_migrations.py --auto-approve --db-path test_data_migration.db
```

### 5. Validate Results
```bash
# Run validation script
python ai_agent_utils/validate_migration.py --db-path test_data_migration.db
```

### 6. Clean Up
```bash
# Remove test database
rm test_data_migration.db
```

## Reporting

### Test Results Documentation
- Document all test cases and their results
- Include any issues found and their resolution
- Provide performance metrics
- Record the time taken for migration on different data sizes

### Issue Tracking
- Log any issues found during testing
- Track issue resolution
- Update migration scripts as needed based on test results

## Best Practices

1. **Always backup** before running migrations on production data
2. **Test with production-like data** volumes and characteristics
3. **Run migrations during low-usage periods** in production
4. **Monitor the migration process** for errors or performance issues
5. **Have a rollback plan** in case the migration fails
6. **Document all migrations** with clear descriptions of changes
7. **Test rollback procedures** before applying migrations to production