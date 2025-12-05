from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta

class EventManager(models.Manager):
    """自定义管理器，提供常用查询方法"""
    def active(self):
        return self.filter(active=True)
    
    def upcoming(self, days=30):
        """获取未来指定天数内的事件"""
        from_date = date.today()
        end_date = from_date + timedelta(days=days)
        events = []
        for event in self.active():
            next_date = event.next_occurrence(from_date)
            if next_date and from_date <= next_date <= end_date:
                events.append((event, next_date))
        # 按日期排序
        events.sort(key=lambda x: x[1])
        return [event[0] for event in events]

class Event(models.Model):
    TYPE_ONE_TIME = "one_time"
    TYPE_ANNUAL = "annual"
    TYPE_REMINDER = "reminder"
    TYPE_MONTHLY_WEEKEND = "monthly_weekend"

    TYPE_CHOICES = [
        (TYPE_ONE_TIME, "一次性提醒"),
        (TYPE_ANNUAL, "每年重复（纪念日/节日）"),
        (TYPE_REMINDER, "提醒（可作为一次性或重复）"),
        (TYPE_MONTHLY_WEEKEND, "每月第N个周末"),
    ]

    WEEK_ORDER_CHOICES = [
        (1, "第1个周末"),
        (2, "第2个周末"),
        (3, "第3个周末"),
        (4, "第4个周末"),
    ]

    name = models.CharField("事件名称", max_length=200)
    description = models.TextField("描述", blank=True, help_text="可选的详细描述")
    event_type = models.CharField(
        "事件类型", 
        max_length=32, 
        choices=TYPE_CHOICES, 
        default=TYPE_ONE_TIME,
        help_text="选择事件的重复类型"
    )
    
    # 日期和时间字段
    date = models.DateField(
        "日期", 
        null=True, 
        blank=True,
        help_text="适用于一次性、年度和提醒类型的事件"
    )
    time = models.TimeField(
        "时间", 
        null=True, 
        blank=True,
        help_text="可选的具体时间"
    )

    # 月度周末相关字段
    week_order = models.PositiveSmallIntegerField(
        "周末顺序",
        choices=WEEK_ORDER_CHOICES, 
        null=True, 
        blank=True,
        help_text="适用于每月第N个周末类型的事件"
    )

    # 状态和元数据
    active = models.BooleanField("启用", default=True, help_text="是否启用此事件")
    priority = models.PositiveSmallIntegerField(
        "优先级",
        default=0,
        help_text="数值越大优先级越高，用于排序"
    )

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = EventManager()

    class Meta:
        app_label = "events"
        verbose_name = "事件"
        verbose_name_plural = "事件"
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        """模型验证"""
        super().clean()
        
        # 根据事件类型验证必填字段
        if self.event_type in [self.TYPE_ONE_TIME, self.TYPE_ANNUAL, self.TYPE_REMINDER]:
            if not self.date:
                raise ValidationError({"date": "此类型事件需要设置日期。"})
        
        if self.event_type == self.TYPE_MONTHLY_WEEKEND:
            if not self.week_order:
                raise ValidationError({"week_order": "每月周末类型事件需要选择周末顺序。"})
            # 清除不相关的字段
            self.date = None
            self.time = None

    def save(self, *args, **kwargs):
        """保存模型"""
        super().save(*args, **kwargs)

    @property
    def event_type_display_with_icon(self):
        """返回带图标的事件类型显示"""
        icons = {
            self.TYPE_ONE_TIME: "📅",
            self.TYPE_ANNUAL: "🔄", 
            self.TYPE_REMINDER: "⏰",
            self.TYPE_MONTHLY_WEEKEND: "📆"
        }
        icon = icons.get(self.event_type, "📌")
        return f"{icon} {self.get_event_type_display()}"

    @property
    def next_occurrence_display(self):
        """返回下次发生的可读字符串"""
        next_date = self.next_occurrence()
        if next_date:
            if self.time:
                return f"{next_date.strftime('%Y-%m-%d')} {self.time.strftime('%H:%M')}"
            return next_date.strftime('%Y-%m-%d')
        return "无下次发生"

    def next_occurrence(self, from_date=None):
        """
        返回从 from_date（含）开始的下一次发生的 date 对象。
        如果无下一次（如一次性事件且已过），返回 None。
        """
        if from_date is None:
            from_date = date.today()
        
        if not self.active:
            return None

        # ONE-TIME 和 REMINDER
        if self.event_type in [self.TYPE_ONE_TIME, self.TYPE_REMINDER]:
            if not self.date:
                return None
            if self.date >= from_date:
                return self.date
            return None

        # ANNUAL: 年度重复
        if self.event_type == self.TYPE_ANNUAL:
            if not self.date:
                return None
            return self._next_annual_occurrence(from_date)

        # MONTHLY_WEEKEND: 每月第N个周末
        if self.event_type == self.TYPE_MONTHLY_WEEKEND:
            if not self.week_order:
                return None
            return self._next_monthly_weekend_occurrence(from_date)

        return None

    def _next_annual_occurrence(self, from_date):
        """计算下次年度发生日期"""
        month = self.date.month
        day = self.date.day
        year = from_date.year
        
        # 尝试今年
        try:
            candidate = date(year, month, day)
        except ValueError:
            # 处理闰年2月29等情况
            year += 1
            try:
                candidate = date(year, month, day)
            except Exception:
                return None
        
        # 如果今年已过，尝试明年
        if candidate < from_date:
            year += 1
            try:
                candidate = date(year, month, day)
            except Exception:
                return None
        
        return candidate

    def _next_monthly_weekend_occurrence(self, from_date):
        """计算下次月度周末发生日期"""
        year = from_date.year
        month = from_date.month
        
        # 搜索未来24个月
        for _ in range(24):
            weekend_start = self._nth_weekend_start(year, month, self.week_order)
            if weekend_start and weekend_start >= from_date:
                return weekend_start
            
            # 进入下个月
            month += 1
            if month > 12:
                month = 1
                year += 1
        
        return None

    @staticmethod
    def _nth_weekend_start(year, month, n):
        """
        返回指定年/月第 n 个周末的周六日期（如果存在）。
        周末定义为周六（5）和周日（6）。返回周六作为该周末的开始。
        """
        if n not in range(1, 5):  # 支持1-4个周末
            return None
            
        # 找到当月第一个周六
        first_day = date(year, month, 1)
        days_to_saturday = (5 - first_day.weekday()) % 7
        first_saturday = first_day + timedelta(days=days_to_saturday)
        
        # 计算第n个周末的周六
        target_saturday = first_saturday + timedelta(weeks=(n-1))
        
        # 确保目标日期仍在当月
        if target_saturday.month == month:
            return target_saturday
        
        return None

    def get_absolute_url(self):
        """返回事件的绝对URL（需要配置URL）"""
        return f"/events/{self.pk}/"
