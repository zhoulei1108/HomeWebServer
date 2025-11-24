#!/bin/bash

# 部署脚本 - 生产环境部署指南

echo "=== 家庭日历系统部署脚本 ==="

# 1. 环境检查
echo "检查Python环境..."
python3 --version || { echo "Python 3 未安装"; exit 1; }

# 2. 虚拟环境设置
echo "设置虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 3. 依赖安装
echo "安装依赖包..."
pip install -r requirements.txt

# 4. 环境变量设置
echo "设置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "请编辑 .env 文件设置正确的 SECRET_KEY 和其他配置"
fi

# 5. 数据库迁移
echo "执行数据库迁移..."
cd myhome_project
python manage.py makemigrations
python manage.py migrate

# 6. 静态文件收集
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 7. 创建超级用户（可选）
echo "如需创建管理员账户，请运行: python manage.py createsuperuser"

# 8. 启动服务
echo "启动Gunicorn服务器..."
gunicorn --bind 0.0.0.0:8000 myhome.wsgi:application

echo "=== 部署完成 ==="