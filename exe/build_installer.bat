@echo off
echo Building Society Management System Installer...

REM Check if makensis is available
makensis /? >nul 2>&1
if %errorlevel% neq 0 (
    echo NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH.
    echo Please download and install NSIS from http://nsis.sourceforge.net
    echo Then run this script again to create the installer.
    pause
    exit /b 1
)

REM Build the installer
makensis installer.nsi

if %errorlevel% equ 0 (
    echo.
    echo Installer created successfully!
    echo The installer can be found in SocietyManagementSystem-Installer.exe
    echo.
    echo To install the application, simply run SocietyManagementSystem-Installer.exe
) else (
    echo.
    echo Failed to create installer. Please check the error messages above.
)

pause