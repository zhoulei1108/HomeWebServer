# MyHome Project

一个基于 Django 的家庭日历和事件管理系统。

## 项目结构

```
myhome_project/
├── manage.py                 # Django 管理脚本
├── requirements.txt          # Python 依赖包
├── db.sqlite3              # SQLite 数据库
├── README.md                # 项目说明文档
├── myhome/                  # Django 项目配置目录
│   ├── __init__.py
│   ├── settings.py          # 项目设置
│   ├── urls.py              # 主 URL 配置
│   ├── wsgi.py              # WSGI 配置
│   └── asgi.py              # ASGI 配置
├── apps/                    # Django 应用目录
│   ├── __init__.py
│   ├── events/              # 事件管理应用
│   │   ├── __init__.py
│   │   ├── admin.py         # 管理后台配置
│   │   ├── apps.py          # 应用配置
│   │   ├── forms.py         # 表单定义
│   │   ├── models.py        # 数据模型
│   │   ├── urls.py          # 应用 URL 配置
│   │   ├── views.py         # 视图函数
│   │   └── migrations/      # 数据库迁移文件
│   └── family_calendar/     # 家庭日历应用
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── urls.py
│       ├── utils.py
│       ├── views.py
│       └── migrations/
├── templates/               # 模板文件目录
│   └── myhome/
│       └── events/          # 事件应用模板
│           ├── create_event.html
│           ├── create_success.html
│           ├── event_detail.html
│           ├── event_list.html
│           └── upcoming_events.html
└── static/                  # 静态文件目录
    └── .gitkeep
```

## 功能特性

- **事件管理**: 支持一次性、年度重复、提醒和月度周末类型的事件
- **家庭日历**: 基础的家庭日历功能
- **管理后台**: 完整的 Django Admin 后台管理
- **响应式界面**: 基于 Bootstrap 的现代化用户界面

## 快速开始

### 1. 激活虚拟环境

```bash
# Windows
..\.venv_django\Scripts\activate.bat

# Linux/Mac
source ../.venv_django/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
python manage.py migrate
```

### 4. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问应用：
- 主页: http://127.0.0.1:8000/
- 事件列表: http://127.0.0.1:8000/events/
- 管理后台: http://127.0.0.1:8000/admin/
- 日历: http://127.0.0.1:8000/calendar/
- 登录页面: http://127.0.0.1:8000/accounts/login/

### 默认管理员账户
- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@example.com`

## 开发说明

### 应用结构

- **events**: 事件管理应用，支持多种事件类型和重复规则
- **family_calendar**: 家庭日历应用，提供基础日历功能

### 数据模型

#### Event 模型
- 支持四种事件类型：一次性、年度重复、提醒、月度周末
- 包含优先级、启用状态等管理字段
- 提供下次发生时间计算功能

### 模板系统

- 使用 Django 模板引擎
- 集成 Bootstrap 样式框架
- 支持模板继承和组件化

## 部署说明

本项目为开发环境配置，生产环境部署请参考 Django 官方文档进行相应配置：

1. 设置 `DEBUG = False`
2. 配置 `ALLOWED_HOSTS`
3. 设置生产环境数据库
4. 配置静态文件服务
5. 设置安全相关配置

## 技术栈

- Python 3.13
- Django 5.2.8
- SQLite (开发环境)
- Bootstrap (前端框架)

## 许可证

MIT License