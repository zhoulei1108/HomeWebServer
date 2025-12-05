#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.housework.models import Housework
from django.contrib.auth.models import User
from datetime import date

def debug_api():
    """调试API问题"""
    print("调试家务API...")
    
    # 获取第一个用户
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("没有找到活跃用户")
        return
    
    print(f"使用用户: {user.username}")
    
    # 创建测试数据
    weekly_housework = Housework.objects.create(
        title='调试每周家务',
        description='每周一、三、五执行',
        user=user,
        planned_date=date(2025, 12, 1),
        planned_duration=30,
        frequency='weekly',
        priority=2,
        status='pending',
        weekdays=[0, 2, 4]
    )
    print(f"   ✓ 创建成功，ID: {weekly_housework.id}")
    
    # 检查查询
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 31)
    
    print(f"\n查询范围: {start_date} 到 {end_date}")
    
    # 查询常规家务
    regular_houseworks = Housework.objects.filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date,
        frequency__in=['once', 'daily', 'monthly']
    )
    print(f"常规家务数量: {regular_houseworks.count()}")
    for hw in regular_houseworks:
        print(f"  - {hw.title} ({hw.planned_date})")
    
    # 查询每周家务
    weekly_houseworks = Housework.objects.filter(frequency='weekly')
    print(f"每周家务数量: {weekly_houseworks.count()}")
    for hw in weekly_houseworks:
        print(f"  - {hw.title}, 重复星期: {hw.weekdays}")
    
    # 测试2025年12月1日
    current_date = date(2025, 12, 1)
    day_weekday = current_date.weekday()
    print(f"\n2025年12月1日是星期{day_weekday+1} (weekday={day_weekday})")
    
    # 检查应该显示的每周家务
    matching_weekly = []
    for weekly_hw in weekly_houseworks:
        if weekly_hw.weekdays and day_weekday in weekly_hw.weekdays:
            matching_weekly.append(weekly_hw)
    
    print(f"12月1日应该显示的每周家务: {len(matching_weekly)} 个")
    for hw in matching_weekly:
        print(f"  - {hw.title}")
    
    # 清理
    weekly_housework.delete()
    print(f"\n✓ 测试数据已清理")

if __name__ == '__main__':
    debug_api()