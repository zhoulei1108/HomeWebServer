@echo off
echo 正在执行数据库迁移...
cd /d "%~dp0\myhome_project"
python manage.py makemigrations toolbox
python manage.py migrate

echo.
echo 迁移完成！按任意键退出...
pause >nul
