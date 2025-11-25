#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from apps.housework.models import Housework, HouseworkCategory
from django.contrib.auth.models import User
from datetime import date, timedelta

# 获取测试用户和分类
user = User.objects.filter(username='admin').first()
categories = list(HouseworkCategory.objects.all())

if user and categories:
    # 创建多个测试家务，分布在当前月份的不同日期
    test_houseworks = [
        {
            'title': '打扫客厅',
            'category': 0,  # 其他
            'date': date.today(),
            'duration': 30,
            'priority': 2
        },
        {
            'title': '洗衣服',
            'category': 1,  # 洗衣整理
            'date': date.today() + timedelta(days=1),
            'duration': 45,
            'priority': 1
        },
        {
            'title': '做晚饭',
            'category': 2,  # 烹饪饮食
            'date': date.today() + timedelta(days=2),
            'duration': 60,
            'priority': 3
        },
        {
            'title': '拖地',
            'category': 0,  # 其他
            'date': date.today() + timedelta(days=3),
            'duration': 20,
            'priority': 2
        },
        {
            'title': '倒垃圾',
            'category': 0,  # 其他
            'date': date.today() + timedelta(days=4),
            'duration': 10,
            'priority': 1
        }
    ]
    
    for hw_data in test_houseworks:
        if hw_data['category'] < len(categories):
            housework = Housework.objects.create(
                title=hw_data['title'],
                description=f'测试家务: {hw_data["title"]}',
                category=categories[hw_data['category']],
                user=user,
                planned_date=hw_data['date'],
                planned_duration=hw_data['duration'],
                priority=hw_data['priority'],
                status='pending'
            )
            print(f"创建家务: {housework.title} - {housework.planned_date} - {categories[hw_data['category']].icon}")
    
    print(f"总共创建了 {len(test_houseworks)} 个测试家务工单")
    print("现在可以在日历月视图中测试家务显示功能")
else:
    print("没有找到用户或分类数据")