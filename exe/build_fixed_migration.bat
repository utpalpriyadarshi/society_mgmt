@echo off
echo Building Society Management System Executable (Fixed Version)...

REM Copy fixed files
echo Copying fixed migration manager...
copy ai_agent_utils\migrations\migration_manager_fixed.py ai_agent_utils\migrations\migration_manager.py /Y

REM Create the executable using the fixed spec file
echo Creating executable with fixed migration handling...
pyinstaller --noconfirm SocietyManagementSystem_fixed.spec

if %errorlevel% equ 0 (
    echo.
    echo Build successful!
    echo The executable can be found in the dist\SocietyManagementSystem.exe
    echo.
    echo To run the application, double-click on dist\SocietyManagementSystem.exe
) else (
    echo.
    echo Build failed. Please check the error messages above.
)

pause