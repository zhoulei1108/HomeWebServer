#!/usr/bin/env python
import os, sys, django

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myhome_project')
sys.path.insert(0, project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from django.contrib.auth.models import User
from apps.family.models import Family, FamilyMember, set_current_family
from apps.housework.models import Housework, HouseworkCategory
from datetime import date

def setup_admin_family():
    """设置admin的家庭和家务"""
    print("=== 设置admin的家庭和家务 ===")
    
    # 获取admin用户
    admin = User.objects.get(username='admin')
    
    # 检查admin的家庭
    admin_families = Family.objects.filter(members__user=admin, members__is_active=True)
    
    if not admin_families.exists():
        print("admin没有家庭，创建默认家庭...")
        family = Family.objects.create(
            name="Admin家庭",
            description="admin的默认家庭",
            color_theme="#a8edea"
        )
        FamilyMember.objects.create(
            family=family,
            user=admin,
            role='owner'
        )
        print(f"创建家庭: {family}")
    else:
        family = admin_families.first()
        print(f"admin已有家庭: {family}")
    
    # 设置为当前家庭
    set_current_family(admin, family)
    print(f"设置当前家庭: {family.name}")
    
    # 创建家务分类
    category, created = HouseworkCategory.objects.get_or_create(
        name="清洁家务",
        defaults={
            'color': '#FF6B6B',
            'icon': '🧹'
        }
    )
    print(f"家务分类: {category.name} (新建:{created})")
    
    # 创建每周重复家务
    weekly_housework, created = Housework.objects.get_or_create(
        title="每周拖地",
        defaults={
            'description': '每周一、三、五拖地',
            'category': category,
            'family': family,
            'user': admin,
            'planned_date': date.today(),
            'planned_duration': 30,
            'frequency': 'weekly',
            'weekdays': [0, 2, 4],  # 周一、三、五 (0=周一)
            'status': 'pending',
            'priority': 2,
        }
    )
    
    if created:
        print(f"创建每周重复家务: {weekly_housework.title}")
        print(f"重复星期: {weekly_housework.weekdays}")
    else:
        print(f"已存在每周重复家务: {weekly_housework.title}")
        # 确保重复设置正确
        if weekly_housework.weekdays != [0, 2, 4]:
            weekly_housework.weekdays = [0, 2, 4]
            weekly_housework.save()
            print(f"更新重复星期为: {weekly_housework.weekdays}")
    
    return admin, family

if __name__ == '__main__':
    admin, family = setup_admin_family()