# 家庭日历系统 - 开发者指南

## 📋 目录
- [环境搭建](#环境搭建)
- [项目结构](#项目结构)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [调试指南](#调试指南)
- [测试指南](#测试指南)
- [部署指南](#部署指南)
- [常见问题](#常见问题)

---

## 🛠️ 环境搭建

### 1. 系统要求
- Python 3.8+
- Git
- 推荐使用 VS Code 或 PyCharm

### 2. 克隆项目
```bash
git clone <repository-url>
cd HomeWebServer
```

### 3. 创建虚拟环境
```bash
# Windows
python -m venv .venv_django
.venv_django\Scripts\activate

# Linux/Mac
python3 -m venv .venv_django
source .venv_django/bin/activate
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置必要的配置
```

### 6. 数据库初始化
```bash
cd myhome_project
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. 启动开发服务器
```bash
# Windows
start_dev.bat

# Linux/Mac
python manage.py runserver
```

---

## 📁 项目结构

```
HomeWebServer/
├── .venv_django/                 # 虚拟环境
├── myhome_project/              # Django 项目主目录
│   ├── apps/                    # 应用模块
│   │   ├── family/              # 家庭管理模块
│   │   ├── events/              # 事件管理模块
│   │   ├── housework/           # 家务管理模块
│   │   └── family_calendar/     # 日历模块
│   ├── static/                   # 静态文件
│   ├── templates/               # 模板文件
│   ├── myhome/                  # 项目配置
│   └── manage.py                # Django 管理脚本
├── templates/                   # 全局模板
├── requirements.txt             # 依赖包列表
├── start_dev.bat               # Windows 启动脚本
└── deploy.sh                   # Linux 部署脚本
```

### 应用模块详解

#### 1. family (家庭管理)
- **models.py**: Family, FamilyMember, UserProfile, Invitation
- **views.py**: 家庭仪表板、成员管理、邀请功能
- **forms.py**: 家庭创建、个人资料表单
- **urls.py**: `/family/` 路由配置

#### 2. events (事件管理)
- **models.py**: Event 事件模型
- **views.py**: 事件CRUD操作
- **forms.py**: 事件创建和编辑表单
- **urls.py**: `/events/` 路由配置

#### 3. housework (家务管理)
- **models.py**: Housework, HouseworkCategory, HouseworkTemplate
- **views.py**: 家务分配、统计功能
- **forms.py**: 家务表单和模板
- **urls.py**: `/housework/` 路由配置

#### 4. family_calendar (日历模块)
- **views.py**: 月视图、日视图
- **templatetags/**: 自定义模板标签

---

## 🔧 开发流程

### 1. Git 工作流
```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 提交代码
git add .
git commit -m "feat: 添加新功能描述"

# 推送分支
git push origin feature/your-feature-name

# 合并到主分支
git checkout main
git merge feature/your-feature-name
```

### 2. 提交信息规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

### 3. 开发步骤
1. **需求分析**: 明确功能需求和技术方案
2. **设计阶段**: 数据库设计、API设计、UI设计
3. **编码实现**: 按照代码规范编写代码
4. **测试验证**: 单元测试、功能测试
5. **代码审查**: 同事审查代码质量
6. **部署上线**: 部署到测试/生产环境

---

## 📝 代码规范

### 1. Python 代码规范
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 行长度不超过 88 字符 (Black 默认)
- 添加类型注解

```python
# 好的例子
from typing import List, Optional
from django.contrib.auth.models import User

def get_family_members(family_id: int) -> List[User]:
    """获取家庭成员列表
    
    Args:
        family_id: 家庭ID
        
    Returns:
        用户对象列表
    """
    return User.objects.filter(
        familymember__family_id=family_id,
        familymember__is_active=True
    )
```

### 2. Django 最佳实践
- 使用 `get_object_or_404` 处理不存在的对象
- 合理使用 `select_related` 和 `prefetch_related`
- 表单验证在模型和表单层都要有
- 使用 `@login_required` 装饰器保护视图

```python
# 好的例子
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@login_required
def family_detail(request, family_id: int):
    """家庭详情页"""
    family = get_object_or_404(
        Family.objects.select_related('created_by'),
        id=family_id,
        members__user=request.user
    )
    
    members = family.members.select_related('user').all()
    
    return render(request, 'family/detail.html', {
        'family': family,
        'members': members,
    })
```

### 3. 数据库规范
- 模型名称使用单数形式
- 字段名称使用下划线分隔的小写字母
- 为查询频繁的字段添加索引
- 使用 `related_name` 设置反向关系

```python
class Housework(models.Model):
    """家务记录模型"""
    
    title = models.CharField("家务标题", max_length=100)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='houseworks',
        verbose_name="负责人"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'planned_date']),
        ]
```

### 4. 模板规范
- 使用中文注释说明模板结构
- 遵循 Bootstrap 5 组件规范
- 使用 `{% load %}` 加载必要的模板标签

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<!-- 家庭管理页面 -->
<div class="container mt-4">
    <div class="row">
        <!-- 家庭信息卡片 -->
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">{{ family.name }}</h5>
                </div>
                <!-- 卡片内容 -->
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🐛 调试指南

### 1. Django Debug Toolbar
```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
```

### 2. 日志调试
```python
import logging

logger = logging.getLogger(__name__)

def some_view(request):
    logger.info("用户访问页面")
    logger.debug(f"用户ID: {request.user.id}")
    logger.error("发生错误", exc_info=True)
```

### 3. 数据库查询调试
```python
# 查看执行的SQL查询
from django.db import connection

def debug_queries():
    # 执行查询
    users = User.objects.all()
    
    # 查看SQL
    for query in connection.queries:
        print(query['sql'])
        print(f"耗时: {query['time']}秒")
```

### 4. 常用调试命令
```bash
# Django shell
python manage.py shell

# 检查项目配置
python manage.py check --deploy

# 数据库迁移状态
python manage.py showmigrations

# 清除缓存
python manage.py clear_cache
```

---

## 🧪 测试指南

### 1. 单元测试
```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from apps.family.models import Family, FamilyMember

class FamilyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.family = Family.objects.create(name='测试家庭')
    
    def test_family_member_creation(self):
        """测试家庭成员创建"""
        member = FamilyMember.objects.create(
            user=self.user,
            family=self.family,
            role='member'
        )
        self.assertEqual(str(member), f"{self.user.username} - {self.family.name}")
        self.assertTrue(member.is_active)
```

### 2. 视图测试
```python
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class FamilyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
    
    def test_dashboard_view(self):
        """测试仪表板视图"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('family:dashboard'))
        self.assertEqual(response.status_code, 200)
```

### 3. 运行测试
```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test apps.family

# 运行特定测试类
python manage.py test apps.family.tests.FamilyModelTest

# 生成测试覆盖率报告
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # 生成HTML报告
```

---

## 🚀 部署指南

### 1. 生产环境准备
```bash
# 使用部署脚本
chmod +x deploy.sh
./deploy.sh

# 或手动部署
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### 2. Gunicorn 配置
```bash
# 启动 Gunicorn
gunicorn -c gunicorn.conf.py myhome.wsgi:application

# 后台运行
nohup gunicorn -c gunicorn.conf.py myhome.wsgi:application &
```

### 3. Nginx 配置
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## ❓ 常见问题

### 1. 开发环境问题

**Q: 启动时提示 "ModuleNotFoundError"**
```bash
A: 检查虚拟环境是否激活，依赖是否安装完整
pip install -r requirements.txt
```

**Q: 数据库迁移失败**
```bash
A: 检查迁移文件状态，重置迁移
python manage.py showmigrations
python manage.py migrate --fake
```

### 2. 功能问题

**Q: 用户无法登录**
```
A: 检查密码验证配置，确认用户存在
python manage.py shell
User.objects.get(username='yourname').check_password('yourpassword')
```

**Q: 静态文件不显示**
```bash
A: 检查 STATIC_URL 和 STATICFILES_DIRS 配置
python manage.py collectstatic --noinput
```

### 3. 性能问题

**Q: 页面加载慢**
```python
A: 检查 N+1 查询问题，添加 select_related
# 优化前
members = FamilyMember.objects.filter(family=family)
# 优化后  
members = FamilyMember.objects.select_related('user').filter(family=family)
```

---

## 📚 学习资源

### Django 官方文档
- [Django 文档](https://docs.djangoproject.com/)
- [Django Girls 教程](https://tutorial.djangogirls.org/)

### Python 相关
- [PEP 8 代码风格指南](https://pep.python.org/pep-0008/)
- [Python 类型注解](https://docs.python.org/3/library/typing.html)

### 前端资源
- [Bootstrap 5 文档](https://getbootstrap.com/docs/)
- [Font Awesome 图标](https://fontawesome.com/)

---

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**最后更新**: 2024-12-10  
**版本**: v1.0