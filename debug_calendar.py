#!/usr/bin/env python
import os, sys, django
from datetime import date
import calendar

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myhome_project')
sys.path.insert(0, project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

def debug_calendar_structure():
    """调试日历结构"""
    print("=== 调试日历结构 ===")
    
    today = date.today()
    year, month = today.year, today.month
    
    print(f"当前日期: {today} (周{['一','二','三','四','五','六','日'][today.weekday()]})")
    
    # 获取月历数据
    cal = calendar.monthcalendar(year, month)
    
    print(f"\n{year}年{month}月月历结构:")
    print("(注: 0表示不属于该月的日期)")
    
    for week_num, week in enumerate(cal):
        print(f"\n第{week_num+1}周: {week}")
        for day_idx, day_num in enumerate(week):
            if day_num == 0:
                print(f"  位置{day_idx}: 空日期")
            else:
                current_date = date(year, month, day_num)
                python_weekday = current_date.weekday()  # 0=周一, 6=周日
                print(f"  位置{day_idx}: {day_num}日, Python weekday={python_weekday}({['一','二','三','四','五','六','日'][python_weekday]})")
    
    print("\n星期对应关系:")
    print("HTML表格列索引: 0=周日, 1=周一, 2=周二, 3=周三, 4=周四, 5=周五, 6=周六")
    print("Python weekday: 0=周一, 1=周二, 2=周三, 3=周四, 4=周五, 5=周六, 6=周日")

if __name__ == '__main__':
    debug_calendar_structure()