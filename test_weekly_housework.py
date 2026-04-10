#!/usr/bin/env python
import os, sys, django

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myhome_project')
sys.path.insert(0, project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from django.contrib.auth.models import User
from apps.family.models import Family, FamilyMember, get_current_family
from apps.housework.models import Housework, HouseworkCategory
from datetime import date, datetime, timedelta
import calendar

def create_weekly_housework_test():
    """创建每周重复家务测试数据"""
    print("=== 创建每周重复家务测试数据 ===")
    
    # 获取用户和家庭
    admin = User.objects.get(username='admin')
    current_family = get_current_family(admin)
    
    if not current_family:
        print("admin没有当前家庭")
        return
    
    print(f"当前家庭: {current_family.name}")
    
    # 创建或获取家务分类
    category, created = HouseworkCategory.objects.get_or_create(
        name="测试家务",
        defaults={
            'color': '#FF6B6B',
            'icon': '🧹'
        }
    )
    
    # 创建一个每周重复的家务（每周一、三、五）
    weekly_housework, created = Housework.objects.get_or_create(
        title="拖地测试",
        defaults={
            'description': '每周一、三、五拖地',
            'category': category,
            'family': current_family,
            'user': admin,
            'planned_date': date.today(),  # 初始计划日期
            'planned_duration': 30,
            'frequency': 'weekly',
            'weekdays': [0, 2, 4],  # 周一、三、五 (0=周一)
            'status': 'pending',
            'priority': 2,
        }
    )
    
    if created:
        print(f"创建每周重复家务: {weekly_housework.title}")
        print(f"重复星期: {weekly_housework.weekdays} (0=周一, 2=周三, 4=周五)")
    else:
        print(f"已存在每周重复家务: {weekly_housework.title}")
        print(f"当前重复星期: {weekly_housework.weekdays}")
        # 更新重复星期以确保正确
        weekly_housework.weekdays = [0, 2, 4]  # 周一、三、五
        weekly_housework.save()
        print(f"更新重复星期为: {weekly_housework.weekdays}")

def test_month_api():
    """测试月度家务API"""
    print("\n=== 测试月度家务API ===")
    
    from django.test import RequestFactory
    from apps.housework.views import get_month_houseworks
    
    # 创建模拟请求
    factory = RequestFactory()
    today = date.today()
    year, month = today.year, today.month
    
    request = factory.get(f'/housework/api/month/?year={year}&month={month}')
    
    # 设置用户
    admin = User.objects.get(username='admin')
    request.user = admin
    
    # 调用API
    response = get_month_houseworks(request)
    
    if response.status_code == 200:
        data = response.content.decode('utf-8')
        import json
        result = json.loads(data)
        
        print(f"API响应状态: 成功")
        print(f"总家务数: {result.get('total_count', 0)}")
        print(f"每周重复家务数: {result.get('weekly_count', 0)}")
        
        houseworks_by_day = result.get('houseworks_by_day', {})
        
        # 调试：打印houseworks_by_day的结构
        print(f"\nhouseworks_by_day结构 (共{len(houseworks_by_day)}天有家务):")
        for day, day_houseworks in houseworks_by_day.items():
            print(f"  {day}日: {len(day_houseworks)}个家务")
            for hw in day_houseworks:
                is_weekly = hw.get('is_weekly', False)
                print(f"    - {hw['title']} (每周重复:{is_weekly})")
        
        # 获取本周的日期
        cal = calendar.monthcalendar(year, month)
        today_day = today.day
        
        print(f"\n当前月份({year}年{month}月)的家务分布:")
        
        # 直接显示有家务的日期
        print(f"\n实际显示的家务:")
        sorted_days = sorted(houseworks_by_day.keys())
        for day_num in sorted_days:
            day_int = int(day_num)  # 转换为整数
            if day_int <= today_day:  # 只显示到今天
                current_date = date(year, month, day_int)
                python_weekday = current_date.weekday()  # 0=周一, 6=周日
                
                day_houseworks = houseworks_by_day[day_num]
                print(f"  {day_int}日(周{['一','二','三','四','五','六','日'][python_weekday]}): {len(day_houseworks)}个家务")
                for hw in day_houseworks:
                    is_weekly = hw.get('is_weekly', False)
                    print(f"    - {hw['title']} (每周重复:{is_weekly})")
    else:
        print(f"API调用失败，状态码: {response.status_code}")

if __name__ == '__main__':
    create_weekly_housework_test()
    test_month_api()