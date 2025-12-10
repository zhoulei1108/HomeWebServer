#!/usr/bin/env python
"""
中国法定节假日检查工具
用于检查特定日期是否为中国法定节假日或工作日调整

依赖: chinese-calendar 库
功能: 判断日期是否为节假日、调休工作日等
"""
import datetime as dt

# 导入中国日历库，用于判断节假日
import chinese_calendar as cc

def check_holidays(dates):
    """
    检查指定日期的节假日状态
    
    Args:
        dates (list): 要检查的日期列表 [datetime.date, ...]
    
    Returns:
        None: 直接打印结果
    """
    print("=== 中国节假日状态检查 ===")
    print("格式: 日期 | 类型 | 详细信息")
    print("-" * 40)
    
    for date in dates:
        try:
            # 获取节假日详细信息
            detail = cc.get_holiday_detail(date)
            date_str = date.isoformat()
            holiday_type = detail.holiday if detail else "工作日"
            detail_info = str(detail) if detail else "普通工作日"
            
            print(f"{date_str} | {holiday_type} | {detail_info}")
            
        except Exception as e:
            print(f"❌ 检查 {date.isoformat()} 时出错: {e}")

if __name__ == '__main__':
    """
    测试用的日期列表
    包含各种特殊情况：清明节、劳动节、周末等
    """
    # 测试日期：2025年4月初的清明节和劳动节相关日期
    test_dates = [
        dt.date(2025, 4, 4),  # 清明节（可能为法定假日）
        dt.date(2025, 4, 5),  # 清明节假期
        dt.date(2025, 4, 6),  # 周末
        dt.date(2025, 5, 1),  # 劳动节
        dt.date(2025, 5, 2),  # 劳动节假期
        dt.date(2025, 5, 3),  # 劳动节假期
    ]
    
    check_holidays(test_dates)

