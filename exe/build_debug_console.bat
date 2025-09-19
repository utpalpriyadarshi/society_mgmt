@echo off
echo Building Society Management System Executable (Debug Version)...

REM Create the executable using the debug spec file
echo Creating debug executable with console output...
pyinstaller --noconfirm SocietyManagementSystem_debug.spec

if %errorlevel% equ 0 (
    echo.
    echo Debug build successful!
    echo The executable can be found in the dist\SocietyManagementSystem.exe
    echo.
    echo To run the application with console output, double-click on dist\SocietyManagementSystem.exe
) else (
    echo.
    echo Debug build failed. Please check the error messages above.
)

pause