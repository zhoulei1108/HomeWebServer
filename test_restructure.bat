@echo off
echo Testing template restructure tools...
echo.

echo 1. Testing Python script existence...
if exist "restructure_templates.py" (
    echo [OK] restructure_templates.py found
) else (
    echo [ERROR] restructure_templates.py not found
    pause
    exit /b 1
)

echo.
echo 2. Testing Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
) else (
    echo [OK] Python is available
)

echo.
echo 3. Running DRY RUN...
python restructure_templates.py --dry-run

echo.
echo Test completed.