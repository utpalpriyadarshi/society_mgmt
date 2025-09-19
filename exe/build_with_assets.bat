@echo off
echo Building Society Management System Executable (With Assets)...

REM Copy fixed files
echo Copying fixed login dialog...
copy gui\login_dialog_fixed.py gui\login_dialog.py /Y

REM Create the executable using the assets spec file
echo Creating executable with assets...
pyinstaller --noconfirm SocietyManagementSystem_assets.spec

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