@echo off
echo 正在启动家庭日历系统...
echo.

cd /d "%~dp0\myhome_project"

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请确保已安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/2] 正在执行数据库迁移...
python manage.py makemigrations toolbox 2>nul
python manage.py migrate

if errorlevel 1 (
    echo [错误] 数据库迁移失败
    pause
    exit /b 1
)

echo.
echo [2/2] 正在启动开发服务器...
echo 访问地址: http://127.0.0.1:8000/
echo.
python manage.py runserver 0.0.0.0:8000

if errorlevel 1 (
    echo [错误] 服务器启动失败
    pause
    exit /b 1
)
