# 家庭日历管理系统

一个基于Django的家庭日历和事件管理系统，支持多种事件类型和农历显示。

## 功能特性

### 📅 日历功能
- 月视图和日视图
- 农历日期显示
- 节日提醒（公历和农历）
- 事件创建和管理

### 🎯 事件类型
- 一次性提醒
- 年度重复（纪念日/节日）
- 提醒事件
- 每月第N个周末

### 👥 用户功能
- 用户认证
- 个人资料管理
- 事件颜色标记

## 技术栈

- **后端**: Django 5.2.8
- **数据库**: SQLite (开发环境)
- **农历支持**: lunardate
- **前端**: Django Templates + HTML/CSS

## 安装和运行

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv .venv_django

# 激活虚拟环境
# Windows
.venv_django\Scripts\activate
# Linux/Mac
source .venv_django/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库初始化
```bash
cd .venv_django/Scripts/myhome
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 3. 运行服务器
```bash
python manage.py runserver
```

访问地址：
- 主页: http://127.0.0.1:8000/
- 管理后台: http://127.0.0.1:8000/admin/
- 日历: http://127.0.0.1:8000/calendar/
- 事件管理: http://127.0.0.1:8000/events/

## 项目结构

```
HomeWebServer/
├── .venv_django/                 # 虚拟环境
│   └── Scripts/myhome/          # Django项目
│       ├── manage.py
│       ├── myhome/              # 项目配置
│       └── apps/                # 应用目录
│           ├── events/          # 事件管理
│           └── family_calendar/ # 家庭日历
├── templates/                   # 全局模板
├── requirements.txt             # 依赖包
├── .gitignore                  # Git忽略文件
└── README.md                   # 项目文档
```

## 开发说明

### 环境变量
生产环境需要设置以下环境变量：
- `SECRET_KEY`: Django密钥
- `DEBUG`: 设为False
- `ALLOWED_HOSTS`: 允许的主机列表

### 数据库
- 开发环境使用SQLite
- 生产环境建议使用PostgreSQL或MySQL

## 许可证

MIT License