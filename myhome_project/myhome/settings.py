"""
Django 项目配置文件 - 家庭日历管理系统
项目描述: 一个集成了家庭管理、事件提醒、家务分配的综合家庭管理系统

Django 版本: 5.2.8
配置说明: 开发环境配置，包含家庭、日历、事件、家务等模块

配置文档:
- Django 官方文档: https://docs.djangoproject.com/en/5.2/topics/settings/
- 完整配置参考: https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# 项目根目录路径
# 所有路径都基于此目录进行相对路径计算
# 指向项目根目录(HomeWebServer)，而不是myhome_project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ==================== 基础安全配置 ====================
# 注意: 以下为开发环境配置，生产环境需要加强安全性
# 生产环境安全检查清单: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

import os
from decouple import config

# Django 安全密钥 (生产环境必须使用环境变量)
# 用于密码哈希、会话签名等安全功能
SECRET_KEY = config('SECRET_KEY', 
    default='django-insecure-^qvk$6u6ks*q3s2i9$574^7_d&v3@hvrgvgbhzslca3t4n!=v=',
    cast=str)

# 调试模式开关 (生产环境必须设置为 False)
# 开发时显示详细错误信息，生产环境显示友好错误页面
DEBUG = config('DEBUG', default=True, cast=bool)

# 允许的主机列表 (生产环境需要配置实际域名)
# 防止 HTTP Host 攻击，限制可访问的主机名
ALLOWED_HOSTS = config('ALLOWED_HOSTS', 
    default='127.0.0.1,localhost,testserver', 
    cast=lambda v: [s.strip() for s in v.split(',')])


# ==================== 应用模块配置 ====================
# Django 应用程序注册列表
# 系统模块 + 自定义业务模块

INSTALLED_APPS = [
    # Django 内置应用
    "django.contrib.admin",           # 后台管理界面
    "django.contrib.auth",             # 用户认证系统
    "django.contrib.contenttypes",      # 内容类型框架
    "django.contrib.sessions",         # 会话管理
    "django.contrib.messages",         # 消息框架
    "django.contrib.staticfiles",      # 静态文件管理
    
    # 家庭管理模块
    "apps.family",                     # 家庭成员和组管理
    "apps.family_calendar",            # 家庭日历功能
    
    # 业务功能模块
    "apps.events.apps.EventsConfig",    # 事件提醒管理
    "apps.housework.apps.HouseworkConfig",  # 家务分配管理
    "apps.toolbox.apps.ToolboxConfig",      # 百宝箱
]

# ==================== 中间件配置 ====================
# 请求处理管道，按顺序执行
# 中间件影响所有视图的请求和响应处理

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",           # 安全中间件 (SSL、HSTS等)
    "django.contrib.sessions.middleware.SessionMiddleware",     # 会话中间件
    "django.middleware.common.CommonMiddleware",               # 通用中间件 (POST处理、URL规范化)
    "django.middleware.csrf.CsrfViewMiddleware",               # CSRF 防护中间件
    "django.contrib.auth.middleware.AuthenticationMiddleware",   # 用户认证中间件
    "django.contrib.messages.middleware.MessageMiddleware",     # 消息中间件
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # 点击劫持防护
]

ROOT_URLCONF = "myhome.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.family.context_processors.family_context",
            ],
            "libraries": {
                # 显式注册自定义模板标签，确保任意环境都能加载
                "dict_extras": "apps.family_calendar.templatetags.dict_extras",
            },
        },
    },
]

WSGI_APPLICATION = "myhome.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
# 暂时禁用密码验证以便测试
AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Login/Logout settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/calendar/'
LOGOUT_REDIRECT_URL = '/calendar/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
