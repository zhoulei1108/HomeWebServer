from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta, date
from calendar import monthcalendar
from apps.events.models import Event
try:
    from chinese_holidays import get_holidays
    HOLIDAYS_AVAILABLE = True
except ImportError:
    HOLIDAYS_AVAILABLE = False


def get_monthly_weekend_dates(year, month, week_order):
    """获取指定月份中第N个周末的日期（周六和周日）"""
    from datetime import timedelta
    
    # 找到当月第一个周六
    first_day = date(year, month, 1)
    days_to_saturday = (5 - first_day.weekday()) % 7
    first_saturday = first_day + timedelta(days=days_to_saturday)
    
    # 计算第N个周末的周六
    target_saturday = first_saturday + timedelta(weeks=(week_order-1))
    
    # 确保目标日期仍在当月
    if target_saturday.month != month:
        return []
    
    # 返回周六和周日
    target_sunday = target_saturday + timedelta(days=1)
    if target_sunday.month == month:
        return [target_saturday, target_sunday]
    else:
        return [target_saturday]


def month_view(request, year=None, month=None):
    """月视图"""
    if year is None:
        year = request.GET.get('year', timezone.now().year)
    if month is None:
        month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = timezone.now().year
        month = timezone.now().month
    
    # 获取该月的日历数据
    cal = monthcalendar(year, month)
    
    # 获取该月的事件 - 使用events应用中的Event模型
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # 获取节假日数据
    holidays = {}
    if HOLIDAYS_AVAILABLE:
        try:
            holidays_data = get_holidays(year)
            for holiday in holidays_data:
                holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
                if holiday_date.month == month:
                    holidays[holiday_date.day] = holiday['name']
        except:
            pass
    
    # 简化的农历数据 - 使用预定义的重要节日
    lunar_festivals = {
        '1-1': '春节',
        '1-15': '元宵节',
        '2-2': '龙抬头',
        '5-5': '端午节',
        '7-7': '七夕节',
        '8-15': '中秋节',
        '9-9': '重阳节',
        '10-1': '寒衣节',
        '10-15': '下元节',
        '12-8': '腊八节',
        '12-23': '小年',
        '12-30': '除夕'
    }
    
    # 简化的农历数据 - 使用预定义的重要节日和简单农历显示
    lunar_data = {}
    
    # 预定义的一些重要农历节日对应的公历日期（2024-2025年）
    predefined_lunar_dates = {
        2024: {
            2: {10: '春节', 24: '元宵节'},
            4: {4: '清明'},
            6: {10: '端午节'},
            8: {18: '中秋节'},
            9: {17: '重阳节'}
        },
        2025: {
            1: {29: '春节', 12: '元宵节'},
            3: {31: '清明'},
            5: {31: '端午节'},
            9: {6: '中秋节'},
            10: {6: '重阳节'}
        }
    }
    
    # 为每一天添加基本的农历日期显示
    for day in range(1, 32):
        try:
            current_date = date(year, month, day)
            # 简单的农历日期计算（显示初一、十五等）
            day_of_month = current_date.day
            
            lunar_day_info = ''
            if day_of_month == 1:
                lunar_day_info = '初一'
            elif day_of_month == 15:
                lunar_day_info = '十五'
            else:
                lunar_day_info = str(day_of_month)
            
            # 检查是否有节日
            festival = ''
            if year in predefined_lunar_dates and month in predefined_lunar_dates[year]:
                if day in predefined_lunar_dates[year][month]:
                    festival = predefined_lunar_dates[year][month][day]
            
            lunar_data[day] = {
                'day': lunar_day_info,
                'festival': festival
            }
        except:
            continue
    
    # 获取所有启用的事件，并计算它们在指定月份的发生情况
    events_by_date = {}
    active_events = Event.objects.active()
    
    for event in active_events:
        # 根据事件类型计算在该月的具体日期
        if event.event_type == Event.TYPE_ONE_TIME:
            # 一次性事件：检查是否在该月
            if event.date and start_date <= event.date <= end_date:
                if event.date not in events_by_date:
                    events_by_date[event.date] = []
                events_by_date[event.date].append(event)
                
        elif event.event_type == Event.TYPE_ANNUAL:
            # 年度事件：检查月日是否匹配
            if event.date:
                try:
                    annual_date = date(year, event.date.month, event.date.day)
                    if start_date <= annual_date <= end_date:
                        if annual_date not in events_by_date:
                            events_by_date[annual_date] = []
                        events_by_date[annual_date].append(event)
                except ValueError:
                    # 处理闰年2月29日等问题
                    pass
                    
        elif event.event_type == Event.TYPE_REMINDER:
            # 提醒事件：检查是否在该月
            if event.date and start_date <= event.date <= end_date:
                if event.date not in events_by_date:
                    events_by_date[event.date] = []
                events_by_date[event.date].append(event)
                
        elif event.event_type == Event.TYPE_MONTHLY_WEEKEND:
            # 每月第N个周末：计算该月的第N个周末
            if event.week_order:
                weekend_dates = get_monthly_weekend_dates(year, month, event.week_order)
                for weekend_date in weekend_dates:
                    if weekend_date not in events_by_date:
                        events_by_date[weekend_date] = []
                    events_by_date[weekend_date].append(event)
    
    # 计算上月下月的日期
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    
    context = {
        'year': year,
        'month': month,
        'calendar': cal,
        'events_by_date': events_by_date,
        'holidays': holidays,
        'lunar_data': lunar_data,
        'month_name': ['一月', '二月', '三月', '四月', '五月', '六月', 
                      '七月', '八月', '九月', '十月', '十一月', '十二月'][month-1],
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    
    return render(request, 'family_calendar/month_view.html', context)


def day_view(request, year, month, day):
    """日视图"""
    try:
        target_date = datetime(year, month, day).date()
    except ValueError:
        return HttpResponse('无效的日期', status=400)
    
    # 获取在指定日期发生的所有事件
    events_on_date = []
    active_events = Event.objects.active()
    
    for event in active_events:
        # 检查事件是否在目标日期发生
        if event.event_type == Event.TYPE_ONE_TIME or event.event_type == Event.TYPE_REMINDER:
            # 一次性或提醒事件
            if event.date == target_date:
                events_on_date.append(event)
                
        elif event.event_type == Event.TYPE_ANNUAL:
            # 年度事件
            if event.date and event.date.month == target_date.month and event.date.day == target_date.day:
                events_on_date.append(event)
                
        elif event.event_type == Event.TYPE_MONTHLY_WEEKEND:
            # 每月第N个周末
            if event.week_order:
                weekend_dates = get_monthly_weekend_dates(year, month, event.week_order)
                if target_date in weekend_dates:
                    events_on_date.append(event)
    
    context = {
        'date': target_date,
        'events': events_on_date,
    }
    
    return render(request, 'family_calendar/day_view.html', context)