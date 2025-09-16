# Data Migration Testing Procedure Usage Guide

## Overview
This guide explains how to use the data migration testing procedure implemented for the Society Management System.

## Components

1. **Testing Procedure Document** (`DATA_MIGRATION_TESTING_PROCEDURE.md`):
   - Comprehensive guide to testing data migrations
   - Covers pre-migration, migration, and post-migration testing
   - Includes best practices and edge case testing

2. **Test Data Population Script** (`ai_agent_utils/populate_test_data.py`):
   - Populates a database with sample data for testing
   - Creates realistic test data for residents, ledger, users, and society tables

3. **Data Validation Script** (`ai_agent_utils/validate_migration.py`):
   - Validates data integrity after migrations
   - Checks that all required columns and tables exist
   - Verifies that data meets business rules

4. **Migration Template** (`ai_agent_utils/migrations/006_template.py`):
   - Template for creating new migrations
   - Provides a starting point for migration development

5. **Test Runner Script** (`ai_agent_utils/run_data_migration_test.py`):
   - Automates the entire data migration testing process
   - Executes all steps of the testing procedure

## Usage

### Running the Complete Test Procedure
To run the complete data migration testing procedure:

```bash
python ai_agent_utils/run_data_migration_test.py
```

This will:
1. Create a test database
2. Apply all migrations
3. Populate with test data
4. Validate data before migration
5. Apply any new migrations
6. Validate data after migration
7. Check transformed data
8. Clean up test files

### Customizing the Test Database Path
To use a custom database path:

```bash
python ai_agent_utils/run_data_migration_test.py --db-path /path/to/test.db
```

### Manual Testing Steps
For manual testing, follow these steps:

1. **Create Test Database**:
   ```bash
   python -c "import sqlite3; conn = sqlite3.connect('test.db'); conn.close()"
   ```

2. **Apply Migrations**:
   ```bash
   python ai_agent_utils/apply_migrations.py --auto-approve --db-path test.db
   ```

3. **Populate Test Data**:
   ```bash
   python ai_agent_utils/populate_test_data.py --db-path test.db
   ```

4. **Validate Before Migration**:
   Manually inspect the data or run queries to verify the current state.

5. **Create New Migration**:
   Create a new migration file in `ai_agent_utils/migrations/` with the next version number.

6. **Apply New Migration**:
   ```bash
   python ai_agent_utils/apply_migrations.py --auto-approve --db-path test.db
   ```

7. **Validate After Migration**:
   ```bash
   python ai_agent_utils/validate_migration.py --db-path test.db
   ```

8. **Check Transformed Data**:
   Run specific queries to verify that data was transformed correctly.

9. **Clean Up**:
   Remove the test database file.

## Creating New Data Migrations

1. Copy the template:
   ```bash
   cp ai_agent_utils/migrations/006_template.py ai_agent_utils/migrations/008_your_migration_name.py
   ```

2. Edit the new file to implement your data transformation.

3. Run the test procedure to verify the migration works correctly.

## Best Practices

1. **Always test with realistic data volumes** to ensure performance is acceptable.

2. **Test edge cases** such as null values, special characters, and boundary conditions.

3. **Verify data integrity** at each step of the process.

4. **Document all migrations** with clear descriptions of what they do.

5. **Keep migrations simple** and focused on a single change.

6. **Test rollback procedures** before applying migrations to production.

7. **Backup production data** before applying migrations.

8. **Monitor the migration process** for errors or performance issues.

## Troubleshooting

If you encounter issues during testing:

1. **Check error messages** for specific details about what went wrong.

2. **Verify database connections** and file paths.

3. **Ensure all dependencies** are installed correctly.

4. **Review migration scripts** for syntax errors or logical issues.

5. **Consult the testing procedure document** for detailed guidance on each step.

## Extending the Testing Framework

The testing framework can be extended by:

1. **Adding new validation checks** to `validate_migration.py`.

2. **Creating more complex test data** in `populate_test_data.py`.

3. **Adding performance testing** to measure migration execution time.

4. **Implementing automated rollback testing**.

5. **Adding integration tests** with the main application.