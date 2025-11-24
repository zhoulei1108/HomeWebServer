#!/usr/bin/env python
"""
检查数据库中的数据问题
"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.venv_django', 'Scripts', 'myhome'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.venv_django', 'Scripts', 'myhome', 'apps'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from apps.events.models import Event

def check_events_data():
    """检查事件数据"""
    print("检查 Event 数据...")
    
    # 检查总记录数
    total_count = Event.objects.count()
    print(f"总记录数: {total_count}")
    
    # 检查 active 字段的问题
    try:
        # 检查 active 为 None 的记录
        none_count = Event.objects.filter(active__isnull=True).count()
        print(f"active 为 None 的记录数: {none_count}")
        
        # 检查 active 为空字符串的记录
        empty_count = Event.objects.filter(active='').count()
        print(f"active 为空字符串的记录数: {empty_count}")
        
        # 显示所有记录的 active 值
        print("所有记录的 active 值:")
        for event in Event.objects.all():
            print(f"  ID: {event.id}, Name: {event.name}, Active: {repr(event.active)} (类型: {type(event.active)})")
            
    except Exception as e:
        print(f"检查 active 字段时出错: {e}")
    
    # 尝试简单的查询
    try:
        print("\n测试简单查询...")
        events = Event.objects.all()[:5]
        print(f"成功查询 {len(events)} 条记录")
        
        for event in events:
            print(f"  事件: {event.name}, active: {event.active}")
            
    except Exception as e:
        print(f"查询时出错: {e}")

if __name__ == '__main__':
    check_events_data()