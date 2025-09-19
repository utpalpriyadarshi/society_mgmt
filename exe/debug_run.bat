@echo off
echo Running Society Management System with console output for debugging...

REM Run the executable with console enabled to see error messages
dist\SocietyManagementSystem.exe

echo.
echo Application exited with error code: %errorlevel%
pause