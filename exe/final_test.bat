@echo off
echo Final Test of Society Management System Executable

REM Delete any existing database file to test fresh initialization
if exist society_management.db (
    echo Deleting existing database file...
    del society_management.db
)

echo.
echo Running the application to test database initialization and login...
echo.
echo INSTRUCTIONS:
echo 1. When the login window appears, use these credentials:
echo    Username: sysadmin
echo    Password: systemadmin
echo 2. If login is successful, the main application window should appear
echo 3. If login fails, check the error messages below
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
if exist society_management.db (
    echo Database file created successfully.
    
    REM Check if sysadmin user exists
    python -c "import sqlite3; conn = sqlite3.connect('society_management.db'); cursor = conn.cursor(); cursor.execute('SELECT username, role FROM users WHERE username = 'sysadmin''); result = cursor.fetchone(); conn.close(); print('Default user found:' if result else 'Default user NOT found'); print(result if result else '')"
) else (
    echo Database file was NOT created.
)

echo.
echo Test completed.
pause