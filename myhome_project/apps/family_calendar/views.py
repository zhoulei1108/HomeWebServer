from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import datetime, timedelta, date
from calendar import monthcalendar, monthrange

from apps.events.models import Event

try:
    from lunardate import LunarDate

    LUNAR_AVAILABLE = True
except ImportError:
    LUNAR_AVAILABLE = False

try:
    import chinese_calendar
    from chinese_calendar.constants import Holiday

    HOLIDAYS_AVAILABLE = True
except ImportError:
    chinese_calendar = None
    Holiday = None
    HOLIDAYS_AVAILABLE = False


LUNAR_DAY_NAMES = {
    1: "初一",
    2: "初二",
    3: "初三",
    4: "初四",
    5: "初五",
    6: "初六",
    7: "初七",
    8: "初八",
    9: "初九",
    10: "初十",
    11: "十一",
    12: "十二",
    13: "十三",
    14: "十四",
    15: "十五",
    16: "十六",
    17: "十七",
    18: "十八",
    19: "十九",
    20: "二十",
    21: "廿一",
    22: "廿二",
    23: "廿三",
    24: "廿四",
    25: "廿五",
    26: "廿六",
    27: "廿七",
    28: "廿八",
    29: "廿九",
    30: "三十",
}

LUNAR_FESTIVALS = {
    (1, 1): "春节",
    (1, 15): "元宵节",
    (2, 2): "龙抬头",
    (5, 5): "端午节",
    (7, 7): "七夕节",
    (8, 15): "中秋节",
    (9, 9): "重阳节",
    (12, 8): "腊八节",
    (12, 24): "小年",
    (12, 30): "除夕",
}


def build_lunar_data(year, month):
    """根据公历年月计算当月农历信息。"""
    if not LUNAR_AVAILABLE:
        return {}

    lunar_data = {}
    _, last_day = monthrange(year, month)
    for day in range(1, last_day + 1):
        try:
            lunar_date = LunarDate.fromSolarDate(year, month, day)
        except ValueError:
            continue

        festival = LUNAR_FESTIVALS.get((lunar_date.month, lunar_date.day), "")
        lunar_data[day] = {
            "day": LUNAR_DAY_NAMES.get(lunar_date.day, str(lunar_date.day)),
            "festival": festival,
        }
    return lunar_data


HOLIDAY_NAME_MAP = {}
if Holiday:
    HOLIDAY_NAME_MAP.update(
        {
            getattr(Holiday, "NewYearsDay", None): "元旦",
            getattr(Holiday, "SpringFestival", None): "春节",
            getattr(Holiday, "QingMingFestival", None): "清明节",
            getattr(Holiday, "LabourDay", None): "劳动节",
            getattr(Holiday, "DragonBoatFestival", None): "端午节",
            getattr(Holiday, "MidAutumnFestival", None): "中秋节",
            getattr(Holiday, "NationalDay", None): "国庆节",
            getattr(Holiday, "NewYearsEve", None): "除夕",
            getattr(Holiday, "LanternFestival", None): "元宵节",
            getattr(Holiday, "ValentinesDay", None): "情人节",
            getattr(Holiday, "ChristmasDay", None): "圣诞节",
        }
    )
    HOLIDAY_NAME_MAP.pop(None, None)


HOLIDAY_STRING_MAP = {
    "new year's day": "元旦",
    "spring festival": "春节",
    "lantern festival": "元宵节",
    "kingming festival": "清明节",
    "qingming festival": "清明节",
    "tomb-sweeping day": "清明节",
    "labour day": "劳动节",
    "dragon boat festival": "端午节",
    "mid-autumn festival": "中秋节",
    "national day": "国庆节",
    "new year's eve": "除夕",
    "valentine's day": "情人节",
    "christmas day": "圣诞节",
}


def build_holiday_map(start_date, end_date):
    """返回指定日期范围内的中国法定节假日。"""
    holidays = {}
    if not HOLIDAYS_AVAILABLE:
        return holidays

    current = start_date
    while current <= end_date:
        is_holiday, holiday_name = chinese_calendar.get_holiday_detail(current)
        if is_holiday and holiday_name:
            label = HOLIDAY_NAME_MAP.get(holiday_name)
            if not label:
                label = getattr(holiday_name, "value", str(holiday_name))
            if isinstance(label, str):
                label = HOLIDAY_STRING_MAP.get(label.lower(), label)
            holidays[current.day] = label
        current += timedelta(days=1)
    return holidays


def _apply_form_control_styles(form):
    """为 Django 表单字段追加 Bootstrap 样式。"""
    for field in form.fields.values():
        current_class = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = (current_class + " form-control").strip()


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
    
    holidays = build_holiday_map(start_date, end_date)
    lunar_data = build_lunar_data(year, month)
    
    # 获取当前用户的家庭
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user) if request.user.is_authenticated else None
    
    # 获取所有启用的事件，并计算它们在指定月份的发生情况
    events_by_date = {}
    events_by_day = {}
    # 只显示当前家庭的事件
    active_events = Event.objects.active()
    if current_family:
        active_events = active_events.filter(family=current_family)
    else:
        # 如果没有家庭，显示空结果
        active_events = Event.objects.none()

    def store_event(target_date, event):
        if target_date not in events_by_date:
            events_by_date[target_date] = []
        events_by_date[target_date].append(event)

        if target_date.year == year and target_date.month == month:
            events_by_day.setdefault(target_date.day, []).append(event)
    
    for event in active_events:
        # 根据事件类型计算在该月的具体日期
        if event.event_type == Event.TYPE_ONE_TIME:
            # 一次性事件：检查是否在该月
            if event.date and start_date <= event.date <= end_date:
                store_event(event.date, event)
                
        elif event.event_type == Event.TYPE_ANNUAL:
            # 年度事件：检查月日是否匹配
            if event.date:
                try:
                    annual_date = date(year, event.date.month, event.date.day)
                    if start_date <= annual_date <= end_date:
                        store_event(annual_date, event)
                except ValueError:
                    # 处理闰年2月29日等问题
                    pass
                    
        elif event.event_type == Event.TYPE_REMINDER:
            # 提醒事件：检查是否在该月
            if event.date and start_date <= event.date <= end_date:
                store_event(event.date, event)
                
        elif event.event_type == Event.TYPE_MONTHLY_WEEKEND:
            # 每月第N个周末：计算该月的第N个周末
            if event.week_order:
                weekend_dates = get_monthly_weekend_dates(year, month, event.week_order)
                for weekend_date in weekend_dates:
                    store_event(weekend_date, event)
    
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
        'events_by_day': events_by_day,
        'holidays': holidays,
        'lunar_data': lunar_data,
        'month_name': ['一月', '二月', '三月', '四月', '五月', '六月', 
                      '七月', '八月', '九月', '十月', '十一月', '十二月'][month-1],
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today': timezone.localdate(),
    }
    
    return render(request, 'calendar/month_view.html', context)


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
    
    # 获取当天的家务数据
    houseworks_on_date = []
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user) if request.user.is_authenticated else None
    
    if current_family:
        from apps.housework.models import Housework
        
        # 获取当天的常规家务（一次性、每日、每月）
        regular_houseworks = Housework.objects.filter(
            family=current_family,
            planned_date=target_date,
            frequency__in=['once', 'daily', 'monthly']
        ).select_related('user', 'category')
        
        for housework in regular_houseworks:
            houseworks_on_date.append({
                'id': housework.id,
                'title': housework.title,
                'abbreviation': housework.abbreviation,
                'user_abbreviation': housework.user_abbreviation,
                'color': housework.display_color,
                'category_icon': housework.category.icon if housework.category else '🏠',
                'status': housework.status,
                'priority': housework.priority,
                'type': 'housework',
                'frequency': housework.frequency,
                'user': housework.user,
                'category': housework.category,
            })
        
        # 获取每周重复的家务
        weekly_houseworks = Housework.objects.filter(
            family=current_family,
            frequency='weekly'
        ).select_related('user', 'category')
        
        day_weekday = target_date.weekday()  # 0=周一, 6=周日
        for weekly_housework in weekly_houseworks:
            # 检查weekdays是否为空或格式不正确
            if not weekly_housework.weekdays:
                continue
                
            # 确保weekdays是整数列表，并且处理可能的字符串格式
            weekdays_list = weekly_housework.weekdays
            if isinstance(weekdays_list, str):
                # 如果是字符串，尝试解析
                try:
                    weekdays_list = eval(weekdays_list) if weekdays_list.startswith('[') else [int(weekdays_list)]
                except:
                    weekdays_list = []
            elif not isinstance(weekdays_list, list):
                weekdays_list = []
            
            # 检查是否在指定的星期几
            # 注意：家务模型中的weekdays使用0=周一,1=周二,...,6=周日的格式
            if day_weekday in weekdays_list:
                houseworks_on_date.append({
                    'id': weekly_housework.id,
                    'title': weekly_housework.title,
                    'abbreviation': weekly_housework.abbreviation,
                    'user_abbreviation': weekly_housework.user_abbreviation,
                    'color': weekly_housework.display_color,
                    'category_icon': weekly_housework.category.icon if weekly_housework.category else '🏠',
                    'status': weekly_housework.status,
                    'priority': weekly_housework.priority,
                    'type': 'housework',
                    'frequency': weekly_housework.frequency,
                    'user': weekly_housework.user,
                    'category': weekly_housework.category,
                })
    
    context = {
        'date': target_date,
        'year': year,
        'month': month,
        'day': day,
        'events': events_on_date,
        'houseworks': houseworks_on_date,
        'current_family': current_family,
    }
    
    return render(request, 'calendar/day_view.html', context)


def register(request):
    """用户注册视图，成功后自动登录并跳转到月视图。"""
    if request.user.is_authenticated:
        return redirect('family_calendar:month_view')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        _apply_form_control_styles(form)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('family_calendar:month_view')
    else:
        form = UserCreationForm()
        _apply_form_control_styles(form)

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """允许 GET/POST 方式退出登录，并跳转到月视图。"""
    if request.method in ("POST", "GET"):
        logout(request)
    return redirect('family_calendar:month_view')