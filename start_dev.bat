@echo off
echo === Django 家庭日历系统启动脚本 ===

REM 检查虚拟环境
if not exist ".venv_django\Scripts\python.exe" (
    echo 错误: 虚拟环境未找到！
    echo 请先运行以下命令创建虚拟环境:
    echo python -m venv .venv_django
    echo .venv_django\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境并启动Django
echo 激活虚拟环境...
call .venv_django\Scripts\activate.bat

echo 进入项目目录...
cd myhome_project

echo 检查Django配置...
python manage.py check

echo 启动开发服务器...
echo 访问地址: http://127.0.0.1:8000/
echo 按 Ctrl+C 停止服务器
echo.

python manage.py runserver

pause