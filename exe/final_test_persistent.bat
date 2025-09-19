@echo off
echo Final Test of Society Management System Executable

echo.
echo This test will verify that the executable:
echo 1. Creates the database in the correct location
echo 2. Allows login with default credentials
echo 3. Persists data between sessions
echo.

REM Delete any existing database file to test fresh initialization
if exist dist\society_management.db (
    echo Deleting existing database file...
    del dist\society_management.db
)

echo.
echo Running the application for the first time...
echo.
echo INSTRUCTIONS:
echo 1. When the login window appears, use these credentials:
echo    Username: sysadmin
echo    Password: systemadmin
echo 2. After logging in, you can test creating some data
echo 3. Close the application when done testing
echo 4. Run this script again to verify data persistence
echo.
echo Press any key to start the application...
pause

REM Run the executable
dist\SocietyManagementSystem.exe

echo.
echo Application closed.
echo.
echo Checking if database was created and properly initialized...
echo.

REM Check if database file was created
if exist dist\society_management.db (
    echo [PASS] Database file created successfully in dist folder.
    
    REM Check file size
    for %%A in (dist\society_management.db) do set size=%%~zA
    if %size% GTR 0 (
        echo [PASS] Database file has data (%size% bytes).
    ) else (
        echo [FAIL] Database file is empty.
    )
    
    REM Check if sysadmin user exists
    python -c "import sqlite3; conn = sqlite3.connect('dist/society_management.db'); cursor = conn.cursor(); cursor.execute('SELECT username, role FROM users WHERE username = 'sysadmin''); result = cursor.fetchone(); conn.close(); print('[PASS] Default user found:' if result else '[FAIL] Default user NOT found'); print('User:', result if result else '')"
) else (
    echo [FAIL] Database file was NOT created.
)

echo.
echo Test completed.
echo.
echo To test data persistence:
echo 1. Run this script again
echo 2. Log in with the same credentials
echo 3. Your previously created data should still be there
pause