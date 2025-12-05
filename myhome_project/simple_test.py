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
from datetime import date, timedelta
from calendar import monthcalendar

def simple_test():
    """简单测试"""
    print("简单测试...")
    
    # 获取第一个用户
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("没有找到活跃用户")
        return
    
    # 创建测试数据
    weekly_housework = Housework.objects.create(
        title='测试每周家务',
        user=user,
        planned_date=date(2025, 12, 1),
        planned_duration=30,
        frequency='weekly',
        priority=2,
        status='pending',
        weekdays=[0, 2, 4]  # 周一、三、五
    )
    
    regular_housework = Housework.objects.create(
        title='测试常规家务',
        user=user,
        planned_date=date(2025, 12, 10),
        planned_duration=45,
        frequency='once',
        priority=3,
        status='pending'
    )
    
    # 模拟月视图逻辑
    year, month = 2025, 12
    start_date = date(year, month, 1)
    end_date = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year + 1, 1, 1) - timedelta(days=1)
    
    # 获取常规家务
    regular_houseworks = Housework.objects.filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date,
        frequency__in=['once', 'daily', 'monthly']
    )
    print(f"常规家务: {regular_houseworks.count()} 个")
    
    # 获取每周家务
    weekly_houseworks = Housework.objects.filter(frequency='weekly')
    print(f"每周家务: {weekly_houseworks.count()} 个")
    
    # 生成日历
    month_days = monthcalendar(year, month)
    houseworks_by_day = {}
    
    for week in month_days:
        for day_num in week:
            if day_num == 0:
                continue
                
            current_date = date(year, month, day_num)
            day_weekday = current_date.weekday()
            
            if day_num not in houseworks_by_day:
                houseworks_by_day[day_num] = []
            
            # 添加常规家务
            day_regular = regular_houseworks.filter(planned_date=current_date)
            for hw in day_regular:
                houseworks_by_day[day_num].append({
                    'title': hw.title,
                    'is_weekly': False,
                })
            
            # 添加每周家务
            for weekly_hw in weekly_houseworks:
                if weekly_hw.weekdays and day_weekday in weekly_hw.weekdays:
                    houseworks_by_day[day_num].append({
                        'title': weekly_hw.title,
                        'is_weekly': True,
                    })
    
    # 显示前10天
    print("\n前10天家务:")
    for day in range(1, 11):
        if day in houseworks_by_day and houseworks_by_day[day]:
            day_name = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'][date(year, month, day).weekday()]
            print(f"{day}日({day_name}): {len(houseworks_by_day[day])}个")
            for hw in houseworks_by_day[day]:
                print(f"  - {hw['title']} {'[每周重复]' if hw['is_weekly'] else ''}")
        else:
            print(f"{day}日: 无家务")
    
    # 清理
    weekly_housework.delete()
    regular_housework.delete()

if __name__ == '__main__':
    simple_test()