# 🏠 家庭日历管理系统

> 一个功能完整的 Django 家庭管理系统，集成了家庭成员管理、事件提醒、家务分配和个人资料管理等功能。

![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

### 📅 日历与事件管理
- **多视图日历**: 月视图和日视图展示
- **农历支持**: 完整的农历日期和节日显示
- **多样化事件类型**:
  - 一次性提醒 (生日、会议等)
  - 年度重复 (纪念日、传统节日)
  - 智能提醒 (可一次性或重复)
  - 月度周末 (每月第N个周末)
- **中国法定节假日**: 自动识别节假日和调休

### 👨‍👩‍👧‍👦 家庭管理
- **家庭成员**: 支持多种角色 (家庭主/管理员/成员)
- **权限控制**: 精细化的功能权限管理
- **邀请系统**: 邀请码和邀请链接两种方式
- **多家庭支持**: 用户可加入多个家庭并切换

### 🏠 家务分配
- **智能分配**: 支持模板化快速创建
- **分类管理**: 清洁、洗衣、烹饪等分类
- **统计分析**: 家务完成情况和耗时统计
- **重复设置**: 支持每日、每周、每月重复

### 👤 个人中心
- **丰富资料**: 头像、性别、生日、偏好设置
- **隐私控制**: 资料公开度自定义
- **通知管理**: 邮件和应用通知开关

## 🛠️ 技术栈

### 后端技术
- **框架**: Django 5.2.8
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: Django 内置认证系统
- **农历**: lunardate + chinese-calendar
- **部署**: Gunicorn + Nginx

### 前端技术
- **模板引擎**: Django Templates
- **UI 框架**: Bootstrap 5.3
- **图标库**: Font Awesome 6.0
- **样式**: 自定义 CSS + 渐变设计

### 开发工具
- **环境管理**: python-decouple
- **静态文件**: whitenoise
- **日志**: Python logging
- **测试**: Django TestCase

## 🚀 快速开始

### 📋 系统要求
- Python 3.8+
- Git
- 8GB+ RAM (推荐)
- 2GB+ 磁盘空间

### 🔧 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd HomeWebServer
```

#### 2. 环境配置
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

#### 3. 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件 (重要!)
```

#### 4. 数据库初始化
```bash
cd myhome_project

# 创建数据库迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建管理员账户
python manage.py createsuperuser
```

#### 5. 启动开发服务器
```bash
# Windows 一键启动
start_dev.bat

# 或手动启动
python manage.py runserver
```

### 🌐 访问应用
- **首页**: http://127.0.0.1:8000/
- **管理后台**: http://127.0.0.1:8000/admin/
- **API 文档**: (开发中)
## 📁 项目结构

```
HomeWebServer/
├── 📄 README.md                   # 项目说明文档
├── 📄 requirements.txt            # Python 依赖包
├── 📄 start_dev.bat              # Windows 启动脚本
├── 📄 deploy.sh                  # Linux 部署脚本
├── 📁 .venv_django/              # Python 虚拟环境
├── 📁 myhome_project/            # Django 主项目目录
│   ├── 📁 apps/                  # 应用模块
│   │   ├── 📁 family/            # 家庭管理模块
│   │   ├── 📁 events/            # 事件管理模块  
│   │   ├── 📁 housework/         # 家务管理模块
│   │   └── 📁 family_calendar/   # 日历模块
│   ├── 📁 static/                # 静态文件
│   ├── 📁 templates/             # 模板文件
│   ├── 📁 myhome/                # 项目配置
│   └── 📄 manage.py              # Django 管理脚本
├── 📁 templates/                 # 全局模板文件
├── 📄 CODE_QUALITY_ANALYSIS.md   # 代码质量分析
├── 📄 DEVELOPER_GUIDE.md         # 开发者指南
└── 📄 OPTIMIZATION_GUIDE.md       # 优化建议指南
```

## 🎯 核心功能模块

### 1. 家庭管理 (family)
- **Family Model**: 家庭组信息、邀请码、设置
- **FamilyMember Model**: 成员关系、角色权限  
- **UserProfile Model**: 用户扩展信息、偏好设置
- **Invitation Model**: 邀请管理、状态追踪

### 2. 事件管理 (events)
- **Event Model**: 多类型事件、重复规则
- **EventManager**: 自定义查询管理器
- **支持类型**:
  - `one_time`: 一次性事件
  - `annual`: 年度重复
  - `reminder`: 智能提醒
  - `monthly_weekend`: 月度周末

### 3. 家务管理 (housework)
- **Housework Model**: 家务记录、状态管理
- **HouseworkCategory Model**: 分类系统
- **HouseworkTemplate Model**: 快速创建模板
- **统计功能**: 完成率、耗时分析

### 4. 日历展示 (family_calendar)
- **月视图**: 整月概览、事件分布
- **日视图**: 单日详细安排
- **农历支持**: 传统节日、节气显示
- **自定义标签**: dict_extras 模板标签
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