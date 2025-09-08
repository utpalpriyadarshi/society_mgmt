# Database Error Handling Testing Usage Guide

## Overview
This document provides instructions on how to use the database error handling testing procedure and test script.

## Prerequisites
1. Python 3.6 or higher installed
2. All dependencies from `requirements.txt` installed
3. The Society Management System database file (`society_management.db`) present

## Running Automated Tests

### 1. Execute the Test Script
Run the database error handling test script:

```bash
python test_database_error_handling.py
```

### 2. Review Test Results
The script will output test results in the following format:
- `[PASS]` for successful tests
- `[FAIL]` for failed tests
- `[SKIP]` for skipped tests
- `[ERROR]` for tests that crashed

### 3. Test Output Example
```
Database Error Handling Tests
========================================
[SETUP] Test database created
Testing custom exception classes...
[PASS] DatabaseError exception works correctly
[PASS] DatabaseConnectionError exception works correctly
[PASS] DatabaseLockError exception works correctly
[PASS] DatabaseCorruptionError exception works correctly
[PASS] DatabasePermissionError exception works correctly
[PASS] DatabaseTimeoutError exception works correctly
Testing database context manager normal operation...
[PASS] Database context manager works normally
Testing database context manager connection error handling...
[PASS] Database context manager correctly handles connection errors
Testing database context manager permission error handling...
[PASS] Database context manager correctly handles permission errors
Testing ResidentManager error handling...
[PASS] ResidentManager works normally
[PASS] ResidentManager correctly handles database connection errors
Testing authentication error handling...
[PASS] Authentication works normally
[SKIP] Authentication error handling test (requires mocking)
Testing session manager error handling...
[PASS] Session manager works normally

Results: 13/14 tests passed

All tests passed! Database error handling features are working correctly.
[CLEANUP] Test database removed
```

## Manual Testing Procedures

### 1. Database File Not Found Test
1. Rename or delete the `society_management.db` file
2. Launch the application: `python main.py`
3. Attempt to login with valid credentials
4. Verify that an appropriate error message is displayed
5. Restore the database file

### 2. Database Permission Error Test
1. Change the permissions of `society_management.db` to deny read access:
   ```bash
   # On Unix/Linux/Mac
   chmod 000 society_management.db
   
   # On Windows (using PowerShell as Administrator)
   icacls society_management.db /deny Everyone:R
   ```
2. Launch the application: `python main.py`
3. Attempt to login with valid credentials
4. Verify that an appropriate error message is displayed
5. Restore the permissions:
   ```bash
   # On Unix/Linux/Mac
   chmod 644 society_management.db
   
   # On Windows (using PowerShell as Administrator)
   icacls society_management.db /grant Everyone:F
   ```

### 3. Database Lock Test
1. Open the database file with another application (e.g., DB Browser for SQLite)
2. Launch the application: `python main.py`
3. Attempt to login with valid credentials
4. Verify that an appropriate error message is displayed
5. Close the other application

## Test Data Preparation

### Creating Test Users
The test database should include users with different roles:
- sysadmin (System Admin)
- testadmin (Admin)
- testtreasurer (Treasurer)
- testviewer (Viewer)

You can add these users using the application's User Management feature or by directly modifying the database.

## Interpreting Test Results

### PASS
The feature is working as expected.

### FAIL
The feature is not working correctly. Check:
1. The implementation of the feature
2. The test procedure
3. The test environment

### SKIP
The test was skipped, usually because:
1. It requires additional setup (e.g., mocking)
2. It's not applicable in the current environment
3. It's temporarily disabled

### ERROR
The test crashed, indicating:
1. A bug in the test script
2. A severe issue in the application code
3. An environmental problem

## Troubleshooting

### Test Script Fails to Run
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check that the `society_management.db` file exists
3. Verify Python version is 3.6 or higher

### Tests Fail Unexpectedly
1. Check the test environment setup
2. Verify the database file is not corrupted
3. Ensure the application code has not been modified in a way that breaks the tests

### Permission Tests Fail on Windows
1. Ensure you're running the command prompt or PowerShell as Administrator
2. Check Windows Defender or other security software is not blocking the operations

## Extending the Tests

### Adding New Test Cases
1. Add new methods to the `DatabaseErrorHandlingTest` class
2. Follow the naming convention `test_feature_name`
3. Add the new test method to the `tests` list in `run_all_tests`
4. Ensure the test returns `True` for pass or `False` for fail

### Modifying Existing Tests
1. Update the test method as needed
2. Ensure the test still follows the return value convention
3. Update any documentation that references the test

## Reporting Issues

When reporting issues found during testing, include:
1. The test that failed
2. The error message or unexpected behavior
3. Steps to reproduce the issue
4. Environment details (OS, Python version, etc.)
5. Any relevant screenshots or logs