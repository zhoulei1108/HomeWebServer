#!/bin/bash

# ===================================================================
# 家庭日历系统 - 生产环境部署脚本
# 
# 功能: 自动化部署 Django 家庭日历系统到生产环境
# 支持: Linux/Unix 环境
# 作者: HomeWebServer Team
# 版本: 2.0
# 更新: 2024-12-10
# ===================================================================

set -e  # 遇到错误立即退出

# 颜色定义，便于输出识别
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 脚本开始
echo "=========================================================="
echo "🏠 家庭日历系统 - 生产环境部署脚本 v2.0"
echo "=========================================================="

# 1. 环境检查
log_info "检查系统环境..."

# 检查 Python 版本 (要求 3.8+)
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_success "Python 版本: $PYTHON_VERSION"
    
    # 验证版本是否满足要求
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        log_success "Python 版本满足要求 (3.8+)"
    else
        log_error "Python 版本过低，需要 3.8 或更高版本"
        exit 1
    fi
else
    log_error "Python 3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查必要的系统命令
for cmd in git pip; do
    if ! command -v $cmd &> /dev/null; then
        log_error "缺少必要命令: $cmd"
        exit 1
    fi
done

# 2. 虚拟环境设置
log_info "设置 Python 虚拟环境..."

VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "创建新的虚拟环境..."
    python3 -m venv $VENV_DIR
    log_success "虚拟环境创建完成"
else
    log_info "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
source $VENV_DIR/bin/activate

# 升级 pip 到最新版本
log_info "升级 pip..."
pip install --upgrade pip

# 3. 依赖安装
log_info "安装 Python 依赖包..."

# 检查 requirements.txt 是否存在
if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt 文件不存在"
    exit 1
fi

# 安装依赖，显示详细信息
pip install -r requirements.txt

log_success "依赖包安装完成"

# 4. 环境变量配置
log_info "配置环境变量..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_warning "已从 .env.example 创建 .env 文件"
        log_warning "请编辑 .env 文件设置正确的配置："
        log_warning "  - SECRET_KEY: 生产环境密钥"
        log_warning "  - DEBUG: 设置为 False"
        log_warning "  - ALLOWED_HOSTS: 设置实际域名"
    else
        log_warning ".env.example 文件不存在，创建基础配置"
        cat > .env << EOF
# Django 配置
SECRET_KEY=django-insecure-$(openssl rand -base64 32 | tr -d '=' | head -c 50)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置 (可选，默认使用 SQLite)
# DATABASE_URL=sqlite:///db.sqlite3

# 其他配置
TIME_ZONE=Asia/Shanghai
LANGUAGE_CODE=zh-hans
EOF
        log_success "已创建基础 .env 配置文件"
    fi
else
    log_success ".env 文件已存在"
fi

# 5. 进入项目目录
cd myhome_project

# 6. Django 项目检查
log_info "检查 Django 配置..."
python manage.py check --deploy

# 7. 数据库迁移
log_info "执行数据库迁移..."

# 创建迁移文件
log_info "检查迁移文件..."
python manage.py makemigrations

# 应用迁移
log_info "应用数据库迁移..."
python manage.py migrate

log_success "数据库迁移完成"

# 8. 静态文件处理
log_info "收集静态文件..."
python manage.py collectstatic --noinput --clear

log_success "静态文件收集完成"

# 9. 数据初始化检查
log_info "检查数据库初始化状态..."

# 检查是否有超级用户
SUPERUSER_EXISTS=$(python manage.py shell -c "
from django.contrib.auth.models import User
print(User.objects.filter(is_superuser=True).exists())
" 2>/dev/null || echo "False")

if [ "$SUPERUSER_EXISTS" = "False" ]; then
    log_warning "未检测到超级用户"
    log_warning "部署后请手动创建管理员账户："
    log_warning "  python manage.py createsuperuser"
else
    log_success "已存在超级用户账户"
fi

# 10. 性能优化检查
log_info "执行基本性能优化..."

# 压缩静态文件
if python manage.py compress --help &> /dev/null; then
    python manage.py compress 2>/dev/null || log_warning "静态文件压缩失败（可能缺少依赖）"
fi

# 11. 生产环境启动配置
log_info "生成 Gunicorn 配置文件..."

if [ ! -f "gunicorn.conf.py" ]; then
    cat > gunicorn.conf.py << EOF
# Gunicorn 生产环境配置
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = None
group = None
tmp_upload_dir = None
logfile = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
errorlog = "-"
accesslog = "-"
proc_name = "home_webserver"
EOF
    log_success "Gunicorn 配置文件已创建"
else
    log_info "Gunicorn 配置文件已存在"
fi

# 12. 启动服务
echo "=========================================================="
log_success "部署配置完成！"
echo "=========================================================="

echo ""
log_info "启动选项："
echo "1. 开发模式: python manage.py runserver"
echo "2. 生产模式: gunicorn -c gunicorn.conf.py myhome.wsgi:application"
echo "3. 后台运行: nohup gunicorn -c gunicorn.conf.py myhome.wsgi:application &"
echo ""

# 检查是否直接启动服务
if [ "$1" = "--start" ]; then
    log_info "启动 Gunicorn 服务器..."
    gunicorn -c gunicorn.conf.py myhome.wsgi:application
else
    log_info "准备就绪！请选择启动方式或传递 --start 参数直接启动"
fi

echo ""
log_success "家庭日历系统部署完成！"
echo "=========================================================="

# 部署完成后的建议
echo ""
log_info "部署后续建议："
echo "1. 配置 Web 服务器 (Nginx/Apache) 作为反向代理"
echo "2. 设置 HTTPS 证书"
echo "3. 配置日志轮转"
echo "4. 设置数据库备份"
echo "5. 配置监控和告警"
echo ""