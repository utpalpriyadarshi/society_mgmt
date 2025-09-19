@echo off
echo Testing Society Management System Executable with Database Initialization...

REM Delete any existing database file to test fresh initialization
if exist society_management.db (
    echo Deleting existing database file...
    del society_management.db
)

REM Run the executable for a few seconds to initialize the database
echo Running the application to initialize database...
echo If the application starts successfully, the database should be initialized with default user.
echo.
echo Press Ctrl+C to stop the application after a few seconds.
echo.

REM Run the executable
dist\SocietyManagementSystem.exe

echo.
echo Checking if database was initialized correctly...
echo.

REM Check if database file was created
if exist society_management.db (
    echo Database file created successfully.
    
    REM Check if sysadmin user exists
    python -c "import sqlite3; conn = sqlite3.connect('society_management.db'); cursor = conn.cursor(); cursor.execute(\"SELECT username, role FROM users WHERE username = 'sysadmin'\"); result = cursor.fetchone(); conn.close(); print('Default user found:' if result else 'Default user NOT found'); print(result if result else '')"
) else (
    echo Database file was NOT created.
)

echo.
echo Test completed.
pause