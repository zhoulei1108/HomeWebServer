from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """个人资料表单"""
    
    # 用户信息字段
    first_name = forms.CharField(max_length=30, required=False, label="姓")
    last_name = forms.CharField(max_length=30, required=False, label="名")
    email = forms.EmailField(required=False, label="邮箱")
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'nickname', 'gender', 'birthday', 'bio',
            'favorite_color', 'favorite_food', 'hobbies', 
            'phone', 'address', 'public_profile',
            'notification_enabled', 'email_notifications'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': '介绍一下自己...'}),
            'hobbies': forms.Textarea(attrs={'rows': 3, 'placeholder': '比如：阅读、运动、音乐、旅行...'}),
            'favorite_color': forms.TextInput(attrs={'type': 'color'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'favorite_food': forms.TextInput(attrs={'placeholder': '比如：火锅、烤肉、寿司...'}),
            'phone': forms.TextInput(attrs={'placeholder': '请输入手机号'}),
            'address': forms.TextInput(attrs={'placeholder': '请输入地址'}),
        }
        labels = {
            'avatar': '头像',
            'nickname': '昵称',
            'gender': '性别',
            'birthday': '生日',
            'bio': '个人简介',
            'favorite_color': '喜欢的颜色',
            'favorite_food': '爱吃的食物',
            'hobbies': '个人爱好',
            'phone': '手机号',
            'address': '地址',
            'public_profile': '公开个人资料',
            'notification_enabled': '启用通知',
            'email_notifications': '邮件通知',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置用户信息初始值
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # 添加CSS类
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # 特殊字段的CSS类
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].widget.attrs['class'] = 'form-control'
        self.fields['hobbies'].widget.attrs['class'] = 'form-control'
        self.fields['favorite_color'].widget.attrs['class'] = 'form-control form-control-color'
        
        # 设置字段的help_text
        self.fields['public_profile'].help_text = "是否允许其他家庭成员查看您的详细资料"
        self.fields['favorite_color'].help_text = "选择您喜欢的颜色"
    
    def save(self, commit=True):
        """保存表单数据"""
        profile = super().save(commit=False)
        
        # 更新用户信息
        if self.instance and self.instance.user:
            user = self.instance.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
        
        if commit:
            profile.save()
        return profile
    
    def clean_email(self):
        """验证邮箱唯一性"""
        email = self.cleaned_data.get('email')
        if email:
            User = self.instance.user.__class__
            queryset = User.objects.exclude(pk=self.instance.user.pk) if self.instance and self.instance.user else User.objects
            if queryset.filter(email=email).exists():
                raise forms.ValidationError("该邮箱已被使用")
        return email


class ProfileSettingsForm(forms.ModelForm):
    """个人设置表单（简版）"""
    
    class Meta:
        model = UserProfile
        fields = ['notification_enabled', 'email_notifications', 'public_profile']
        labels = {
            'notification_enabled': '启用通知',
            'email_notifications': '邮件通知',
            'public_profile': '公开个人资料',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-check-input'
            if hasattr(field.widget, 'type') and field.widget.type == 'checkbox':
                field.widget.attrs['class'] = 'form-check-input'