from django import forms
from django.contrib.auth.models import User
from .models import Housework, HouseworkCategory, HouseworkTemplate
from django.utils import timezone
from datetime import date, timedelta


class HouseworkForm(forms.ModelForm):
    """家务记录表单"""
    
    # 自定义星期几选择字段
    weekday_selection = forms.MultipleChoiceField(
        choices=Housework.WEEKDAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='重复星期'
    )
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        self.current_family = kwargs.pop('current_family', None)
        super().__init__(*args, **kwargs)
        
        # 设置字段标签
        self.fields['title'].label = '家务标题'
        self.fields['description'].label = '详细描述'
        self.fields['category'].label = '分类'
        self.fields['user'].label = '负责人'
        self.fields['planned_date'].label = '计划执行日期'
        self.fields['planned_duration'].label = '预计耗时(分钟)'
        self.fields['frequency'].label = '重复频率'
        self.fields['priority'].label = '优先级'
        self.fields['status'].label = '状态'
        self.fields['weekday_selection'].label = '重复星期'
        
        # 限制用户选择为当前家庭的成员
        if self.current_family:
            self.fields['user'].queryset = User.objects.filter(
                id__in=self.current_family.get_active_members().values_list('user', flat=True)
            )
    
    class Meta:
        model = Housework
        fields = [
            'title', 'description', 'category', 'user', 'planned_date',
            'planned_duration', 'frequency', 'weekday_selection', 'priority', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '输入家务标题',
                'autofocus': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '详细描述（可选）'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'planned_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'planned_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 480,
                'step': 5
            }),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        """重写save方法以处理weekdays字段"""
        instance = super().save(commit=False)
        
        # 自动关联家庭
        if self.current_family:
            instance.family = self.current_family
        
        # 处理weekdays字段
        frequency = self.cleaned_data.get('frequency')
        if frequency == 'weekly':
            weekdays = self.cleaned_data.get('weekday_selection', [])
            instance.weekdays = [int(day) for day in weekdays] if weekdays else []
        else:
            instance.weekdays = []
        
        if commit:
            instance.save()
        return instance
        
        # 如果是编辑模式，设置星期几的初始值
        if self.instance.pk and self.instance.weekdays:
            self.fields['weekday_selection'].initial = self.instance.weekdays
        
        # 过滤用户列表（如果有当前用户，优先显示）
        if user:
            self.fields['user'].queryset = User.objects.filter(
                is_active=True
            ).order_by('username')
            if not self.instance.pk:  # 新建记录
                self.fields['user'].initial = user
        
        # 设置默认日期
        if not self.instance.pk and not self.initial.get('planned_date'):
            self.fields['planned_date'].initial = date.today()
    
    def clean_planned_date(self):
        """验证计划日期"""
        planned_date = self.cleaned_data['planned_date']
        if planned_date < date.today():
            raise forms.ValidationError('计划执行日期不能是过去的日期')
        return planned_date
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        frequency = cleaned_data.get('frequency')
        weekdays = cleaned_data.get('weekday_selection')
        actual_duration = getattr(self.instance, 'actual_duration', None)
        
        if status == 'completed' and not actual_duration and not self.instance.pk:
            # 对于新建记录，如果状态是已完成，需要提供实际耗时
            raise forms.ValidationError('已完成的家务必须填写实际耗时')
        
        # 验证每周重复的设置
        if frequency == 'weekly':
            if not weekdays or len(weekdays) == 0:
                raise forms.ValidationError('每周重复的家务必须选择至少一个星期几')
        
        return cleaned_data


class HouseworkCompleteForm(forms.ModelForm):
    """完成家务表单"""
    
    class Meta:
        model = Housework
        fields = ['actual_duration']
        widgets = {
            'actual_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 480,
                'step': 5,
                'placeholder': '实际耗时（分钟）'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['actual_duration'].label = '实际耗时(分钟)'
        self.fields['actual_duration'].required = True


class HouseworkTemplateForm(forms.ModelForm):
    """家务模板表单"""
    
    class Meta:
        model = HouseworkTemplate
        fields = [
            'title', 'description', 'category', 'default_duration',
            'priority', 'frequency'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '模板标题',
                'autofocus': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'default_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 480,
                'step': 5
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # 设置字段标签
        self.fields['title'].label = '模板标题'
        self.fields['description'].label = '描述'
        self.fields['category'].label = '分类'
        self.fields['default_duration'].label = '默认预计耗时(分钟)'
        self.fields['priority'].label = '优先级'
        self.fields['frequency'].label = '重复频率'


class HouseworkFilterForm(forms.Form):
    """家务筛选表单"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='负责人'
    )
    
    category = forms.ModelChoiceField(
        queryset=HouseworkCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='分类'
    )
    
    status = forms.ChoiceField(
        choices=[('', '全部')] + Housework.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='状态'
    )
    
    priority = forms.ChoiceField(
        choices=[('', '全部')] + Housework.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='优先级'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='开始日期'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='结束日期'
    )
    
    def __init__(self, *args, **kwargs):
        self.current_family = kwargs.pop('current_family', None)
        super().__init__(*args, **kwargs)
        
        # 限制用户选择为当前家庭的成员
        if self.current_family:
            self.fields['user'].queryset = User.objects.filter(
                id__in=self.current_family.get_active_members().values_list('user', flat=True)
            )
        
        # 设置默认日期范围（当前月份）
        if not args and not kwargs.get('data'):
            today = date.today()
            first_day = today.replace(day=1)
            if today.month == 12:
                last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            self.fields['date_from'].initial = first_day
            self.fields['date_to'].initial = last_day