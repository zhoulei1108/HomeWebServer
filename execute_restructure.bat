@echo off
chcp 65001 >nul
REM Template directory restructuring execution script
REM For Windows environment automation

echo ============================================================
echo Home Calendar System - Template Restructure Tool
echo ============================================================
echo.

REM Check Python environment
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed or not in PATH
    pause
    exit /b 1
)

REM Check script file
if not exist "restructure_templates.py" (
    echo ERROR: restructure_templates.py script not found
    pause
    exit /b 1
)

echo Please select execution mode:
echo 1. DRY RUN - Analyze only, don't modify files (Recommended first)
echo 2. Execute restructure - Actually modify files and directory structure
echo 3. View detailed help
echo 4. Exit
echo.

set /p choice="Please enter option (1-4): "

if "%choice%"=="1" goto dry_run
if "%choice%"=="2" goto execute
if "%choice%"=="3" goto help
if "%choice%"=="4" goto end

echo ❌ 无效选项，请重新选择
goto :eof

:dry_run
echo.
echo Starting DRY RUN mode...
echo WARNING: This will not modify any files, only show what will be done
echo.
python restructure_templates.py --dry-run
echo.
echo DRY RUN completed
echo Please check the output results, confirm no issues before selecting option 2
goto end

:execute
echo.
echo WARNING: About to execute actual template restructure operation
echo RECOMMEND: Execute DRY RUN (option 1) first to confirm operation
echo.
set /p confirm="Confirm execute restructure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled
    goto end
)

echo.
echo Starting template restructure execution...
echo Creating backup...
echo.

python restructure_templates.py

if errorlevel 1 (
    echo.
    echo Error occurred during restructure
    echo Please check error messages and fix manually
) else (
    echo.
    echo Template restructure completed successfully!
    echo Detailed report generated: template_restructure_report.json
    echo RECOMMEND next steps:
    echo    1. Run development server test: start_dev.bat
    echo    2. Check all pages display correctly
    echo    3. Verify functionality is complete
    echo    4. Restore from backup if issues occur
)

goto end

:help
echo.
echo Template Restructure Tool Help
echo.
echo Features:
echo   - Analyze current template file distribution
echo   - Resolve template file conflicts
echo   - Unify directory structure
echo   - Update template path references in code
echo.
echo Target Structure:
echo   templates/
echo   ├── base.html
echo   ├── registration/
echo   ├── family/
echo   ├── events/
echo   ├── housework/
echo   └── calendar/
echo.
echo Options:
echo   --dry-run    : Show operations only, don't execute modifications
echo   --no-backup  : Skip backup creation (not recommended)
echo.
echo Usage Examples:
echo   python restructure_templates.py --dry-run
echo   python restructure_templates.py
echo.
echo IMPORTANT NOTES:
echo   1. Recommend commit all code changes to Git before execution
echo   2. First-time users must execute DRY RUN first
echo   3. Tool automatically creates backup directory
echo   4. Restore from backup if issues occur

goto end

:end
echo.
echo ============================================================
echo Operation completed
echo ============================================================
pause