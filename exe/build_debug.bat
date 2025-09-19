@echo off
echo Building Society Management System Executable (Debug Version)...

REM Create the executable using the debug spec file
echo Creating debug executable...
pyinstaller --noconfirm SocietyManagementSystem_debug.spec

if %errorlevel% equ 0 (
    echo.
    echo Debug build successful!
    echo The executable can be found in the dist\SocietyManagementSystem folder
    echo.
    echo To run the application and see error messages, run dist\SocietyManagementSystem.exe from the command line
) else (
    echo.
    echo Debug build failed. Please check the error messages above.
)

pause