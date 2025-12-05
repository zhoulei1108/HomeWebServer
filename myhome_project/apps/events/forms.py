from django import forms
from django.utils import timezone
from .models import Event

class EventForm(forms.ModelForm):
    """事件表单，支持动态字段验证和用户友好的界面"""
    
    # 添加自定义字段来接收动态表单数据
    date_one_time = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_annual = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_reminder = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    time_one_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}))
    time_annual = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}))
    time_reminder = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}))
    week_order_monthly = forms.IntegerField(required=False)
    
    class Meta:
        model = Event
        fields = [
            "name", "description", "event_type", 
            "date", "time", "week_order", 
            "active", "priority"
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "输入事件名称",
                "autofocus": True
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "可选的详细描述"
            }),
            "event_type": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control"
            }),
            "week_order": forms.Select(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "priority": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 10,
                "placeholder": "0-10，数值越大优先级越高"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 设置字段标签和帮助文本
        self.fields['name'].label = "事件名称"
        self.fields['description'].label = "描述"
        self.fields['event_type'].label = "事件类型"
        self.fields['date'].label = "日期"
        self.fields['time'].label = "时间"
        self.fields['week_order'].label = "周末顺序"
        self.fields['active'].label = "启用"
        self.fields['priority'].label = "优先级"
        
        # 显式设置字段required属性
        self.fields['name'].required = True
        self.fields['event_type'].required = True
        self.fields['priority'].required = False  # 有默认值，所以不是必填
        self.fields['description'].required = False
        self.fields['date'].required = False
        self.fields['time'].required = False
        self.fields['week_order'].required = False
        self.fields['active'].required = False

    def clean(self):
        """表单级别的验证"""
        cleaned = super().clean()
        event_type = cleaned.get("event_type")
        
        # 根据事件类型从对应的动态字段获取日期和时间
        event_date = None
        event_time = None
        
        if event_type == Event.TYPE_ONE_TIME:
            event_date = cleaned.get("date_one_time")
            event_time = cleaned.get("time_one_time")
        elif event_type == Event.TYPE_ANNUAL:
            event_date = cleaned.get("date_annual")
            event_time = cleaned.get("time_annual")
        elif event_type == Event.TYPE_REMINDER:
            event_date = cleaned.get("date_reminder")
            event_time = cleaned.get("time_reminder")
        elif event_type == Event.TYPE_MONTHLY_WEEKEND:
            week_order = cleaned.get("week_order_monthly")
            if not week_order:
                self.add_error("week_order_monthly", "每月周末类型事件需要选择周末顺序。")
            # 设置正确的字段值
            cleaned['week_order'] = week_order
            cleaned['date'] = None
            cleaned['time'] = None
            return cleaned

        # 设置日期和时间到正确的字段
        if event_date:
            cleaned['date'] = event_date
        if event_time:
            cleaned['time'] = event_time

        # 根据事件类型验证必填字段
        if event_type in [Event.TYPE_ONE_TIME, Event.TYPE_ANNUAL, Event.TYPE_REMINDER]:
            if not event_date:
                self.add_error("date", "此类型事件需要设置日期。")
            else:
                # 验证日期不能是过去的日期（对于一次性事件）
                if event_type == Event.TYPE_ONE_TIME and event_date < timezone.now().date():
                    self.add_error("date", "一次性事件的日期不能是过去的日期。")

        # 验证时间逻辑
        if event_time and not event_date:
            self.add_error("time", "设置了时间就必须同时设置日期。")

        # 清除周末顺序（如果不是每月周末类型）
        if event_type != Event.TYPE_MONTHLY_WEEKEND:
            cleaned['week_order'] = None

        return cleaned

    def clean_name(self):
        """验证事件名称"""
        name = self.cleaned_data.get('name')
        if name:
            # 去除首尾空格
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("事件名称至少需要2个字符。")
            if len(name) > 200:
                raise forms.ValidationError("事件名称不能超过200个字符。")
        return name

    def clean_priority(self):
        """验证优先级"""
        priority = self.cleaned_data.get('priority')
        if priority is not None and (priority < 0 or priority > 10):
            raise forms.ValidationError("优先级必须在0-10之间。")
        return priority


class EventFilterForm(forms.Form):
    """事件筛选表单"""
    
    event_type = forms.ChoiceField(
        choices=[('', '全部类型')] + Event.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    active = forms.ChoiceField(
        choices=[
            ('', '全部状态'),
            ('true', '启用'),
            ('false', '禁用')
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    date_from = forms.DateField(
        label="开始日期",
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )
    
    date_to = forms.DateField(
        label="结束日期",
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )

    def clean(self):
        """验证日期范围"""
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("开始日期不能晚于结束日期。")
        
        return cleaned
