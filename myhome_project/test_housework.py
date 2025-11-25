#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from apps.housework.models import Housework, HouseworkCategory
from django.contrib.auth.models import User

# 获取或创建测试用户
user, created = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
if created:
    user.set_password('admin123')
    user.save()
    print("创建了管理员用户: admin/admin123")

# 获取第一个分类
category = HouseworkCategory.objects.first()
if category:
    # 创建一个测试家务
    housework = Housework.objects.create(
        title='打扫客厅',
        description='清理客厅的桌面和地面',
        category=category,
        user=user,
        planned_date='2025-11-25',
        planned_duration=30,
        priority=2,
        status='pending'
    )
    print(f"创建家务工单: {housework.title} (ID: {housework.id})")
    print(f"分类: {category.name} {category.icon}")
    print(f"访问地址: http://127.0.0.1:8000/housework/{housework.id}/")
    
    # 测试缩写功能
    print(f"家务缩写: {housework.abbreviation}")
    print(f"用户缩写: {housework.user_abbreviation}")
    print(f"显示颜色: {housework.display_color}")
else:
    print("没有找到家务分类，请先运行 init_housework.py")