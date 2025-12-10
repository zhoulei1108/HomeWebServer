#!/usr/bin/env python
import os, sys, django

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myhome_project')
sys.path.insert(0, project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from django.contrib.auth.models import User
from apps.family.models import get_current_family
from apps.housework.models import Housework
from datetime import date

def debug_housework_data():
    """调试家务数据"""
    print("=== 调试家务数据 ===")
    
    # 获取用户和家庭
    admin = User.objects.get(username='admin')
    current_family = get_current_family(admin)
    
    print(f"用户: {admin.username}")
    print(f"当前家庭: {current_family.name if current_family else '无'}")
    
    # 获取所有家务
    houseworks = Housework.objects.filter(family=current_family)
    print(f"\n总家务数: {houseworks.count()}")
    
    for hw in houseworks:
        print(f"\n家务: {hw.title}")
        print(f"  ID: {hw.id}")
        print(f"  频率: {hw.frequency}")
        print(f"  重复星期: {hw.weekdays} (类型: {type(hw.weekdays)})")
        print(f"  计划日期: {hw.planned_date}")
        print(f"  状态: {hw.status}")
        print(f"  用户: {hw.user.username}")
    
    # 专门检查每周重复的家务
    weekly_houseworks = houseworks.filter(frequency='weekly')
    print(f"\n每周重复家务数: {weekly_houseworks.count()}")
    
    for hw in weekly_houseworks:
        print(f"\n每周家务: {hw.title}")
        print(f"  ID: {hw.id}")
        print(f"  重复星期: {hw.weekdays}")
        print(f"  星期类型: {type(hw.weekdays)}")
        print(f"  长度: {len(hw.weekdays) if hw.weekdays else 0}")
        
        # 检查特定日期是否匹配
        test_dates = [
            date(2025, 12, 1),  # 周一
            date(2025, 12, 2),  # 周二  
            date(2025, 12, 3),  # 周三
            date(2025, 12, 4),  # 周四
            date(2025, 12, 5),  # 周五
        ]
        
        for test_date in test_dates:
            weekday = test_date.weekday()  # 0=周一, 6=周日
            should_show = hw.weekdays and weekday in hw.weekdays
            print(f"    {test_date}(周{['一','二','三','四','五','六','日'][weekday]}): 应显示={should_show}")

if __name__ == '__main__':
    debug_housework_data()