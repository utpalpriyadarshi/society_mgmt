@echo off
echo Testing Society Management System Executable...

REM Run the executable and capture output
echo Running the application...
echo If the application starts successfully, you should see the login window.
echo.
echo Press Ctrl+C to stop the application if it starts successfully.
echo.
echo If there are any errors, they will be displayed below:
echo ----------------------------------------------------

REM Run the executable
dist\SocietyManagementSystem.exe

echo.
echo ----------------------------------------------------
echo Test completed.
pause