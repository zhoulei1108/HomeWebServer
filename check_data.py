#!/usr/bin/env python
"""
数据库数据检查工具
用于检查数据库中的数据一致性和完整性问题
"""
import os
import sys
import django

# 添加项目路径到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.venv_django', 'Scripts', 'myhome'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.venv_django', 'Scripts', 'myhome', 'apps'))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from apps.events.models import Event

def check_events_data():
    """
    检查事件数据完整性和一致性
    
    主要检查内容：
    1. 总记录数统计
    2. active字段的数据类型和值分布
    3. 数据查询功能测试
    """
    print("=== 开始检查 Event 数据 ===")
    
    # 1. 检查总记录数
    total_count = Event.objects.count()
    print(f"📊 总记录数: {total_count}")
    
    # 2. 检查 active 字段的数据质量问题
    try:
        print("\n🔍 检查 active 字段状态:")
        
        # 检查 active 为 None 的记录（可能的数据问题）
        none_count = Event.objects.filter(active__isnull=True).count()
        print(f"  - active 为 None 的记录数: {none_count}")
        
        # 检查 active 为空字符串的记录
        empty_count = Event.objects.filter(active='').count()
        print(f"  - active 为空字符串的记录数: {empty_count}")
        
        # 统计 active 字段的值分布
        active_true = Event.objects.filter(active=True).count()
        active_false = Event.objects.filter(active=False).count()
        print(f"  - active=True 的记录数: {active_true}")
        print(f"  - active=False 的记录数: {active_false}")
        
        # 显示问题记录的详细信息
        if none_count > 0 or empty_count > 0:
            print("\n⚠️  发现问题记录:")
            for event in Event.objects.filter(active__isnull=True) | Event.objects.filter(active=''):
                print(f"  ID: {event.id}, Name: {event.name}, Active: {repr(event.active)} (类型: {type(event.active)})")
        
    except Exception as e:
        print(f"❌ 检查 active 字段时出错: {e}")
    
    # 3. 测试基本查询功能
    try:
        print("\n🧪 测试基本查询功能:")
        events = Event.objects.all()[:5]
        print(f"  成功查询 {len(events)} 条记录")
        
        for event in events:
            print(f"  - 事件: {event.name}, active: {event.active}, 创建时间: {event.created_at}")
            
    except Exception as e:
        print(f"❌ 查询测试时出错: {e}")
    
    # 4. 检查事件类型分布
    try:
        print("\n📈 事件类型分布:")
        from django.db.models import Count
        type_stats = Event.objects.values('event_type').annotate(count=Count('id'))
        for stat in type_stats:
            print(f"  - {stat['event_type']}: {stat['count']} 条")
    except Exception as e:
        print(f"❌ 统计事件类型时出错: {e}")

if __name__ == '__main__':
    """
    脚本入口点
    执行数据检查任务
    """
    check_events_data()
    print("\n✅ 数据检查完成!")