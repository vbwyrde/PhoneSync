@echo off
REM ========================================
REM PhoneSync Batch File Wrapper
REM This batch file runs the PowerShell script for organizing photos and videos
REM Can be scheduled in Windows Task Scheduler
REM ========================================

REM Set the script directory (where this batch file is located)
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Log the start time
echo [%date% %time%] Starting PhoneSync...

REM Check if PowerShell script exists
if not exist "PhoneSync.ps1" (
    echo ERROR: PhoneSync.ps1 not found in %SCRIPT_DIR%
    echo Please ensure the PowerShell script is in the same directory as this batch file.
    pause
    exit /b 1
)

REM Check if configuration file exists
if not exist "config.json" (
    echo ERROR: config.json not found in %SCRIPT_DIR%
    echo Please ensure the configuration file is in the same directory as this batch file.
    pause
    exit /b 1
)

REM Run the PowerShell script with execution policy bypass
REM This allows the script to run even if execution policy is restricted
powershell.exe -ExecutionPolicy Bypass -File "PhoneSync.ps1" -ConfigPath "config.json"

REM Capture the exit code from PowerShell
set PS_EXIT_CODE=%ERRORLEVEL%

REM Log the completion
if %PS_EXIT_CODE% equ 0 (
    echo [%date% %time%] PhoneSync completed successfully.
) else (
    echo [%date% %time%] PhoneSync completed with errors. Exit code: %PS_EXIT_CODE%
)

REM Uncomment the line below if you want the window to stay open for debugging
REM pause

REM Exit with the same code as PowerShell
exit /b %PS_EXIT_CODE%
