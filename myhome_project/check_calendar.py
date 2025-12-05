import calendar
from datetime import date

year = 2025
month = 12
cal = calendar.monthcalendar(year, month)
print(f'{year}年{month}月日历:')
for i, week in enumerate(cal):
    print(f'第{i+1}周: {week}')
    for day in week:
        if day != 0:
            d = date(year, month, day)
            print(f'  {day}日 - 星期{d.weekday()+1} (weekday={d.weekday()})')