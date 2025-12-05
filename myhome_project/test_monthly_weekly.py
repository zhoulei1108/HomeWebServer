#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.housework.models import Housework
from apps.housework.views import get_month_houseworks
from django.contrib.auth.models import User
from django.http import HttpRequest
from datetime import date
from unittest.mock import Mock

def test_monthly_weekly_display():
    """测试月视图中的每周家务显示"""
    print("测试月视图中的每周家务显示...")
    
    # 获取第一个用户
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("没有找到活跃用户，请先创建用户")
        return
    
    print(f"使用用户: {user.username}")
    
    # 清理之前的测试数据
    Housework.objects.filter(user=user, title__contains='测试').delete()
    
    # 创建一个每周重复的家务（周一、周三、周五）
    print("\n1. 创建每周重复家务:")
    weekly_housework = Housework.objects.create(
        title='测试每周家务',
        description='每周一、三、五执行',
        user=user,
        planned_date=date(2025, 12, 1),  # 初始日期
        planned_duration=30,
        frequency='weekly',
        priority=2,
        status='pending',
        weekdays=[0, 2, 4]  # 周一、周三、周五
    )
    print(f"   ✓ 创建成功，ID: {weekly_housework.id}")
    print(f"   ✓ 重复星期: {weekly_housework.weekdays}")
    
    # 创建一个常规家务
    print("\n2. 创建常规家务:")
    regular_housework = Housework.objects.create(
        title='测试常规家务',
        description='只执行一次',
        user=user,
        planned_date=date(2025, 12, 10),
        planned_duration=45,
        frequency='once',
        priority=3,
        status='pending'
    )
    print(f"   ✓ 创建成功，ID: {regular_housework.id}")
    
    # 测试获取12月的家务数据
    print("\n3. 测试获取2025年12月的家务数据:")
    
    # 创建模拟请求
    request = HttpRequest()
    request.method = 'GET'
    request.user = user
    request.GET = {'year': '2025', 'month': '12'}
    
    # 调用API函数 - 直接创建请求对象
    from django.http import QueryDict
    from django.http import HttpRequest
    
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
            self.user = user
            self.GET = {'year': '2025', 'month': '12'}
    
    request = MockRequest()
    
    try:
        response = get_month_houseworks(request)
        import json
        data = json.loads(response.content.decode('utf-8'))
        
        print(f"   ✓ API调用成功")
        print(f"   ✓ 总家务数: {data.get('total_count')}")
        print(f"   ✓ 每周家务数: {data.get('weekly_count')}")
        print(f"   ✓ 每日家务数据: {len(data.get('houseworks_by_day', {}))}")
        
        # 检查特定日期的家务
        houseworks_by_day = data.get('houseworks_by_day', {})
        
        # 显示前10天的详细数据
        print(f"   ✓ 前10天的家务详情:")
        for day in range(1, 11):
            if day in houseworks_by_day:
                day_houseworks = houseworks_by_day[day]
                print(f"      {day}日: {len(day_houseworks)}个家务")
                for hw in day_houseworks:
                    print(f"         - {hw['title']} (优先级:{hw['priority']}) {'[每周重复]' if hw.get('is_weekly') else ''}")
            else:
                print(f"      {day}日: 无家务")
        
        # 验证每周重复逻辑
        print(f"\n   ✓ 验证每周重复逻辑:")
        weekly_days = [1, 3, 5, 8, 10, 15, 17, 19, 22, 24, 26, 29]  # 2025年12月中的周一、三、五
        
        for day in weekly_days:
            if day <= 31 and day in houseworks_by_day:
                day_houseworks = houseworks_by_day[day]
                weekly_count = sum(1 for hw in day_houseworks if hw.get('is_weekly'))
                print(f"      {day}日: 应该有每周家务，实际有 {weekly_count} 个")
        
    except Exception as e:
        print(f"   ✗ API调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据
        weekly_housework.delete()
        regular_housework.delete()
        print("\n   ✓ 测试数据已清理")

if __name__ == '__main__':
    test_monthly_weekly_display()