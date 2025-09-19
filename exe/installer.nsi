; Society Management System Installer Script
; This script will create an installer for the Society Management System

!define APP_NAME "Society Management System"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "NextGen Advisors"
!define APP_DESCRIPTION "A desktop application for managing residential society operations"

; Define the output file name
OutFile "SocietyManagementSystem-Installer.exe"

; Define the default installation directory
InstallDir "$PROGRAMFILES\${APP_NAME}"

; Define the default registry key
InstallDirRegKey HKCU "Software\${APP_NAME}" ""

; Request application privileges for Windows Vista and higher
RequestExecutionLevel admin

; Include Modern UI
!include "MUI2.nsh"

; Define MUI Settings
!define MUI_ABORTWARNING

; Define the installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "EXECUTABLE_README.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Define the uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Define language
!insertmacro MUI_LANGUAGE "English"

; Define the installer sections
Section "MainSection" SEC01
  ; Set output path to the installation directory
  SetOutPath "$INSTDIR"
  
  ; Put file there
  File "dist_package\SocietyManagementSystem.exe"
  File "dist_package\EXECUTABLE_README.txt"
  File "dist_package\StartApplication.bat"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\SocietyManagementSystem.exe"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\Start Application.lnk" "$INSTDIR\StartApplication.bat"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Desktop shortcut
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\SocietyManagementSystem.exe"
SectionEnd

; Define the uninstaller section
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\SocietyManagementSystem.exe"
  Delete "$INSTDIR\EXECUTABLE_README.txt"
  Delete "$INSTDIR\StartApplication.bat"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Start Application.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  
  ; Desktop shortcut
  Delete "$DESKTOP\${APP_NAME}.lnk"
  
  ; Remove directories
  RMDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\${APP_NAME}"
SectionEnd

; Define the installer functions
Function .onInit
  ; Display a warning message
  MessageBox MB_OK "This will install ${APP_NAME} on your computer."
FunctionEnd