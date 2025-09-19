@echo off
echo Building Society Management System Executable (Final Version)...

REM Copy fixed files
echo Copying fixed files...
copy main_fixed.py main.py /Y
copy database_fixed.py database.py /Y
copy ai_agent_utils\migrations\001_initial_schema_fixed.py ai_agent_utils\migrations\001_initial_schema.py /Y

REM Create the executable using the final spec file
echo Creating executable with all fixes...
pyinstaller --noconfirm SocietyManagementSystem_final.spec

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