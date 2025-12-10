# 🚀 模板目录结构重构执行计划

## 📋 执行前检查结果

### ✅ 当前状态
- **总模板文件数**: 35个
- **发现的依赖错误**: 5个 (缺失模板)
- **警告数量**: 0个
- **主要问题**: 视图引用了不存在的模板文件

### ❌ 发现的问题模板
1. `family/profile_settings.html` - 缺失
2. `family/profile_public.html` - 缺失  
3. `family/search_family.html` - 缺失
4. `housework/template_list.html` - 缺失
5. `housework/create_template.html` - 缺失

---

## 🎯 重构目标

### 最终目录结构
```
templates/
├── base.html                    # 基础模板
├── _user_nav.html              # 用户导航组件
├── _includes/                  # 可重用组件 (新增)
├── registration/               # 认证相关
│   ├── login.html
│   ├── register.html
│   └── logged_out.html
├── family/                    # 家庭管理
│   ├── dashboard.html
│   ├── profile.html
│   ├── profile_settings.html    # 需创建
│   ├── profile_public.html      # 需创建
│   ├── create_family.html
│   ├── search_family.html      # 需创建
│   ├── family_detail.html
│   ├── invitation_list.html
│   ├── invite_member.html
│   ├── manage_members.html
│   └── no_family.html
├── events/                    # 事件管理
│   ├── create_event.html
│   ├── create_success.html
│   ├── event_detail.html
│   ├── event_list.html
│   ├── upcoming_events.html
│   └── delete_confirm.html
├── housework/                 # 家务管理
│   ├── create_housework.html
│   ├── edit_housework.html
│   ├── housework_detail.html
│   ├── housework_list.html
│   ├── statistics.html
│   ├── template_list.html      # 需创建
│   └── create_template.html    # 需创建
└── calendar/                  # 日历视图
    ├── month_view.html
    └── day_view.html
```

---

## 📝 Phase 1: 修复缺失模板

### 1.1 创建缺失的 Family 模板

#### profile_settings.html
```html
{% extends "base.html" %}
{% load static %}

{% block title %}个人设置 - 家庭日历{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-cog"></i> 个人设置
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {% if form.non_field_errors %}
                            <div class="alert alert-danger">
                                {% for error in form.non_field_errors %}
                                    {{ error }}
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% for field in form %}
                            <div class="mb-3">
                                <label for="{{ field.id_for_label }}" class="form-label">
                                    {{ field.label }}
                                </label>
                                {{ field }}
                                {% if field.errors %}
                                    <div class="text-danger">
                                        {% for error in field.errors %}
                                            <small>{{ error }}</small>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                                {% if field.help_text %}
                                    <small class="form-text text-muted">{{ field.help_text }}</small>
                                {% endif %}
                            </div>
                        {% endfor %}
                        
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> 保存设置
                        </button>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">快速导航</h6>
                </div>
                <div class="card-body">
                    <a href="{% url 'family:profile' %}" class="btn btn-outline-primary btn-sm mb-2">
                        <i class="fas fa-user"></i> 个人资料
                    </a><br>
                    <a href="{% url 'family:dashboard' %}" class="btn btn-outline-secondary btn-sm">
                        <i class="fas fa-home"></i> 返回主页
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### profile_public.html
```html
{% extends "base.html" %}
{% load static %}

{% block title %}{{ profile.display_name }} 的公开资料 - 家庭日历{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header text-center">
                    <img src="{{ profile.avatar_url }}" class="rounded-circle" width="80" height="80">
                    <h4 class="mt-3">{{ profile.display_name }}</h4>
                    <p class="text-muted">
                        {% if profile.bio %}
                            {{ profile.bio }}
                        {% else %}
                            这个用户很懒，还没有写个人简介
                        {% endif %}
                    </p>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>基本信息</h6>
                            <p>
                                <strong>性别:</strong>
                                {{ profile.get_gender_display|default:"未设置" }}
                            </p>
                            {% if profile.age %}
                            <p><strong>年龄:</strong> {{ profile.age }} 岁</p>
                            {% endif %}
                            {% if profile.favorite_color %}
                            <p>
                                <strong>喜欢的颜色:</strong>
                                <span class="badge" style="background-color: {{ profile.favorite_color }}">
                                    {{ profile.favorite_color }}
                                </span>
                            </p>
                            {% endif %}
                        </div>
                        <div class="col-md-6">
                            <h6>兴趣爱好</h6>
                            {% if profile.favorite_food %}
                            <p><strong>爱吃的食物:</strong> {{ profile.favorite_food }}</p>
                            {% endif %}
                            {% if profile.hobbies %}
                            <p><strong>个人爱好:</strong> {{ profile.hobbies|linebreaks }}</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### search_family.html
```html
{% extends "base.html" %}
{% load static %}

{% block title %}搜索家庭 - 家庭日历{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-search"></i> 搜索家庭
                    </h5>
                </div>
                <div class="card-body">
                    <form method="get">
                        <div class="input-group mb-3">
                            <input type="text" name="q" class="form-control" 
                                   placeholder="输入家庭名称..." 
                                   value="{{ request.GET.q }}">
                            <button class="btn btn-primary" type="submit">
                                <i class="fas fa-search"></i> 搜索
                            </button>
                        </div>
                    </form>
                    
                    {% if families %}
                    <div class="mt-4">
                        <h6>搜索结果</h6>
                        {% for family in families %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="card-title mb-1">{{ family.name }}</h6>
                                        <p class="card-text text-muted small mb-0">
                                            {{ family.description|default:"暂无描述" }}
                                        </p>
                                        <small class="text-muted">
                                            成员数: {{ family.get_member_count }}/{{ family.max_members }}
                                        </small>
                                    </div>
                                    <a href="{% url 'family:join_by_code' %}?code={{ family.invite_code }}" 
                                       class="btn btn-outline-primary btn-sm">
                                        申请加入
                                    </a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    {% if request.GET.q %}
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> 
                        没有找到包含 "{{ request.GET.q }}" 的家庭
                    </div>
                    {% else %}
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> 
                        请输入家庭名称进行搜索
                    </div>
                    {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 1.2 创建缺失的 Housework 模板

#### template_list.html
```html
{% extends "base.html" %}
{% load static %}

{% block title %}家务模板 - 家庭日历{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4><i class="fas fa-clipboard-list"></i> 家务模板</h4>
                <a href="{% url 'housework:create_template' %}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> 创建模板
                </a>
            </div>
            
            {% if templates %}
                <div class="row">
                    {% for template in templates %}
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">{{ template.title }}</h6>
                                <p class="card-text small text-muted">
                                    {{ template.description|default:"无描述" }}
                                </p>
                                <div class="d-flex justify-content-between align-items-center">
                                    <small>
                                        {% if template.category %}
                                            <span class="badge" style="background-color: {{ template.category.color }}">
                                                {{ template.category.name }}
                                            </span>
                                        {% endif %}
                                        预计耗时: {{ template.default_duration }}分钟
                                    </small>
                                    <div>
                                        <a href="{% url 'housework:create' %}?template_id={{ template.id }}" 
                                           class="btn btn-sm btn-outline-success">
                                            <i class="fas fa-plus"></i> 使用
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> 
                    还没有家务模板，<a href="{% url 'housework:create_template' %}">立即创建</a>
                </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

#### create_template.html
```html
{% extends "base.html" %}
{% load static %}

{% block title %}创建家务模板 - 家庭日历{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-plus"></i> 创建家务模板
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {% if form.non_field_errors %}
                            <div class="alert alert-danger">
                                {% for error in form.non_field_errors %}
                                    {{ error }}
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% for field in form %}
                            <div class="mb-3">
                                <label for="{{ field.id_for_label }}" class="form-label">
                                    {{ field.label }}
                                </label>
                                {{ field }}
                                {% if field.errors %}
                                    <div class="text-danger">
                                        {% for error in field.errors %}
                                            <small>{{ error }}</small>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                                {% if field.help_text %}
                                    <small class="form-text text-muted">{{ field.help_text }}</small>
                                {% endif %}
                            </div>
                        {% endfor %}
                        
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> 创建模板
                            </button>
                            <a href="{% url 'housework:template_list' %}" class="btn btn-secondary">
                                <i class="fas fa-arrow-left"></i> 返回
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 📋 Phase 2: 执行重构

### 2.1 执行步骤

1. **运行依赖检查** (已完成)
   ```bash
   python check_template_dependencies.py
   ```

2. **创建缺失模板** (需要手动创建上述模板文件)

3. **运行重构工具**
   ```bash
   # Windows
   execute_restructure.bat
   
   # Linux/Mac  
   ./execute_restructure.sh
   ```

### 2.2 测试验证

重构完成后，执行以下测试：

1. **启动开发服务器**
   ```bash
   start_dev.bat
   # 或
   python manage.py runserver
   ```

2. **功能测试清单**
   - [ ] 用户登录/注册页面正常显示
   - [ ] 家庭仪表板页面正常
   - [ ] 个人资料页面正常
   - [ ] 事件管理页面正常
   - [ ] 家务管理页面正常
   - [ ] 日历视图正常

3. **依赖关系验证**
   ```bash
   python check_template_dependencies.py
   # 确认无错误
   ```

---

## 🔧 预期的代码修改

### views.py 文件修改

#### events/views.py
```python
# 修改前
return safe_render(request, "myhome/events/create_event.html", {...})

# 修改后  
return safe_render(request, "events/create_event.html", {...})
```

#### family_calendar/views.py
```python
# 修改前
return render(request, "family_calendar/month_view.html", context)

# 修改后
return render(request, "calendar/month_view.html", context)
```

### 模板继承关系检查

需要验证以下模板的继承路径是否正确：
- `{% extends "base.html" %}` - 基础模板
- `{% extends "family/base_family.html" %}` - 可能需要调整为 `{% extends "base.html" %}`

---

## 📊 重构收益评估

### 预期收益
1. **文件统一性**: 消除3个位置的重复模板
2. **维护便利性**: 所有模板集中在一个目录
3. **命名一致性**: 统一的应用名称作为目录名
4. **开发效率**: 查找和修改模板更便捷

### 风险缓解
1. **自动备份**: 重构工具自动创建备份
2. **依赖检查**: 提前发现并修复缺失模板
3. **分步执行**: 可以分阶段验证每个模块
4. **回滚方案**: 备份目录可快速恢复

---

## ⏰ 执行时间安排

### 建议执行时间
- **非工作时间**: 周末或晚间
- **团队协调**: 确保无其他开发正在进行重要修改

### 预估时间
- **Phase 1** (创建缺失模板): 1小时
- **Phase 2** (执行重构): 30分钟
- **Phase 3** (测试验证): 1小时
- **总计**: 2.5小时

---

## ✅ 执行前最终检查清单

### 环境准备
- [ ] 代码已提交到版本控制
- [ ] 当前工作目录干净 (无未提交的修改)
- [ ] 备份重要数据

### 工具准备  
- [ ] `restructure_templates.py` 脚本就绪
- [ ] `check_template_dependencies.py` 测试通过
- [ ] 执行脚本权限设置正确

### 文件准备
- [ ] 缺失的5个模板文件已创建
- [ ] 确认备份目录有足够空间
- [ ] 测试数据准备就绪

---

**创建时间**: 2024-12-10  
**状态**: 准备就绪，等待执行  
**下一步**: 创建缺失模板文件，然后执行重构