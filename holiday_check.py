import datetime as dt

import chinese_calendar as cc

dates = [dt.date(2025, 4, 4), dt.date(2025, 4, 5), dt.date(2025, 5, 1), dt.date(2025, 4, 6)]
for d in dates:
    detail = cc.get_holiday_detail(d)
    print(d.isoformat(), detail)

