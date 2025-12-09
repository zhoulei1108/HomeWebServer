#!/usr/bin/env python
"""
Django Shell 脚本：验证家庭系统功能
在项目目录下运行：python manage.py shell < test_system.py
"""
import os
import sys

from django.contrib.auth.models import User
from apps.family.models import Family, FamilyMember, UserProfile, get_current_family, set_current_family
from apps.events.models import Event
from apps.housework.models import Housework, HouseworkCategory

def test_family_system():
    print("=== 测试家庭系统功能 ===")
    
    # 1. 检查现有用户
    users = User.objects.all()
    print(f"现有用户数量: {users.count()}")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")
    
    if users.count() == 0:
        print("没有用户，创建测试用户...")
        test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"创建测试用户: {test_user.username}")
    else:
        test_user = users.first()
        print(f"使用现有用户: {test_user.username}")
    
    # 2. 检查用户的家庭状态
    try:
        profile = test_user.family_profile
        current_family = profile.current_family
        print(f"用户当前家庭: {current_family.name if current_family else '无'}")
    except UserProfile.DoesNotExist:
        print("用户档案不存在，创建档案...")
        UserProfile.objects.create(user=test_user)
        current_family = None
    
    # 3. 检查或创建测试家庭
    families = Family.objects.filter(members__user=test_user, members__is_active=True)
    if families.exists():
        family = families.first()
        print(f"用户已加入家庭: {family.name}")
    else:
        print("用户没有家庭，创建测试家庭...")
        family = Family.objects.create(
            name='测试家庭',
            description='这是一个测试家庭',
            max_members=5
        )
        FamilyMember.objects.create(
            family=family,
            user=test_user,
            role='owner'
        )
        set_current_family(test_user, family)
        print(f"创建家庭并设置用户为: {family.name}")
    
    # 4. 测试获取当前家庭
    current_family = get_current_family(test_user)
    print(f"get_current_family() 返回: {current_family.name if current_family else 'None'}")
    
    # 5. 检查事件数据
    events = Event.objects.filter(family=current_family) if current_family else Event.objects.none()
    print(f"当前家庭的事件数量: {events.count()}")
    
    # 6. 检查家务数据
    if current_family:
        houseworks = Housework.objects.filter(family=current_family)
        print(f"当前家庭的家务数量: {houseworks.count()}")
        
        # 创建默认分类
        from apps.housework.models import create_default_categories
        create_default_categories()
        categories = HouseworkCategory.objects.all()
        print(f"家务分类数量: {categories.count()}")
    
    # 7. 测试数据隔离
    print("\n=== 测试数据隔离功能 ===")
    if current_family:
        # 创建测试事件
        test_event = Event.objects.create(
            name='测试事件',
            family=current_family,
            creator=test_user,
            start_time='2024-01-01 10:00:00',
            end_time='2024-01-01 11:00:00'
        )
        print(f"创建测试事件: {test_event.name}")
        
        # 创建测试家务
        default_category = HouseworkCategory.objects.first()
        if default_category:
            test_housework = Housework.objects.create(
                title='测试家务',
                family=current_family,
                user=test_user,
                category=default_category
            )
            print(f"创建测试家务: {test_housework.title}")
    
    print("\n=== 家庭系统状态检查完成 ===")
    return test_user, current_family

# 执行测试
test_user, current_family = test_family_system()
print(f"\n测试完成！")
print(f"测试用户: {test_user.username}")
print(f"当前家庭: {current_family.name if current_family else '无'}")