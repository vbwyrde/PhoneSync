@echo off
echo Running File Existence Validation...
echo =====================================

REM Change to the project root directory (two levels up from Scripts)
cd /d "%~dp0\..\.."

REM Show current directory for debugging
echo Current directory: %CD%

REM Check if config.yaml exists
if not exist "config.yaml" (
    echo ERROR: config.yaml not found in %CD%
    echo Please run this script from the PhoneSync project root directory
    pause
    exit /b 1
)

REM Run the validation script
python VideoProcessor/Scripts/validate_files_existence.py

echo.
echo Validation complete! Check the file_existence_report.json for details.
pause
