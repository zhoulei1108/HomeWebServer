@echo off
echo Starting template restructure execution...
echo.

echo Creating backup and executing...
python restructure_templates.py

if errorlevel 1 (
    echo.
    echo ERROR occurred during restructure
    echo Please check error messages
) else (
    echo.
    echo SUCCESS: Template restructure completed!
    echo.
    echo Next steps:
    echo 1. Test: start_dev.bat
    echo 2. Check pages: http://127.0.0.1:8000/
    echo 3. Run dependency check: python check_template_dependencies.py
)

echo.
pause