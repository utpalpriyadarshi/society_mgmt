@echo off
echo Building Society Management System Executable...

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install PyInstaller
)

REM Create the executable using the spec file
echo Creating executable...
pyinstaller --noconfirm SocietyManagementSystem.spec

if %errorlevel% equ 0 (
    echo.
    echo Build successful!
    echo The executable can be found in the dist\SocietyManagementSystem folder
    echo.
    echo To run the application, double-click on dist\SocietyManagementSystem\SocietyManagementSystem.exe
) else (
    echo.
    echo Build failed. Please check the error messages above.
)

pause