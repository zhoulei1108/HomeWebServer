from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import random


class HouseworkCategory(models.Model):
    """家务分类"""
    name = models.CharField("分类名称", max_length=50)
    color = models.CharField("显示颜色", max_length=7, default="#007bff", help_text="十六进制颜色代码")
    icon = models.CharField("图标", max_length=2, default="🏠", help_text="用emoji表示")
    description = models.TextField("描述", blank=True)
    
    class Meta:
        verbose_name = "家务分类"
        verbose_name_plural = "家务分类"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Housework(models.Model):
    """家务记录"""
    
    STATUS_CHOICES = [
        ('pending', '待完成'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('skipped', '已跳过'),
    ]
    
    PRIORITY_CHOICES = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
        (4, '紧急'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', '一次性'),
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
    ]
    
    # 基本信息
    title = models.CharField("家务标题", max_length=100)
    description = models.TextField("详细描述", blank=True)
    category = models.ForeignKey(HouseworkCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="分类")
    
    # 关联用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="负责人")
    
    # 时间相关
    planned_date = models.DateField("计划执行日期")
    planned_duration = models.PositiveIntegerField("预计耗时(分钟)", default=30, help_text="单位：分钟")
    actual_duration = models.PositiveIntegerField("实际耗时(分钟)", null=True, blank=True, help_text="单位：分钟")
    
    # 重复性设置
    frequency = models.CharField("重复频率", max_length=10, choices=FREQUENCY_CHOICES, default='once')
    
    # 状态和优先级
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.PositiveSmallIntegerField("优先级", choices=PRIORITY_CHOICES, default=2)
    
    # 时间戳
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)
    
    class Meta:
        verbose_name = "家务记录"
        verbose_name_plural = "家务记录"
        ordering = ['planned_date', '-priority', 'created_at']
        indexes = [
            models.Index(fields=['user', 'planned_date']),
            models.Index(fields=['status', 'planned_date']),
            models.Index(fields=['category', 'planned_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.planned_date})"
    
    def clean(self):
        """验证数据"""
        if self.planned_date < date.today():
            raise ValidationError("计划执行日期不能是过去的日期")
        
        if self.status == 'completed' and not self.actual_duration:
            raise ValidationError("已完成的家务必须填写实际耗时")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def abbreviation(self):
        """返回家务标题的缩写（用于月视图显示）"""
        # 提取中文关键词作为缩写
        if len(self.title) <= 4:
            return self.title
        
        # 常见家务关键词
        keywords = ['打扫', '清洁', '洗衣', '做饭', '购物', '整理', '收拾', '拖地', '洗碗', '倒垃圾']
        for keyword in keywords:
            if keyword in self.title:
                return keyword
        
        # 如果没有关键词，取前2个字
        return self.title[:2]
    
    @property
    def user_abbreviation(self):
        """返回用户名的缩写"""
        username = self.user.username
        if len(username) <= 2:
            return username.upper()
        return username[:2].upper()
    
    @property
    def display_color(self):
        """获取显示颜色"""
        if self.category and self.category.color:
            return self.category.color
        
        # 根据用户分配默认颜色
        user_colors = {
            1: '#FF6B6B',  # 红
            2: '#4ECDC4',  # 青
            3: '#45B7D1',  # 蓝
            4: '#96CEB4',  # 绿
            5: '#FECA57',  # 黄
        }
        user_id = self.user.id % 5 + 1
        return user_colors.get(user_id, '#007bff')
    
    def mark_completed(self, actual_duration=None):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if actual_duration:
            self.actual_duration = actual_duration
        self.save()
    
    def get_duration_difference(self):
        """获取时间差（实际-预计）"""
        if not self.actual_duration:
            return None
        return self.actual_duration - self.planned_duration


class HouseworkTemplate(models.Model):
    """家务模板，用于快速创建重复性家务"""
    
    title = models.CharField("模板标题", max_length=100)
    description = models.TextField("描述", blank=True)
    category = models.ForeignKey(HouseworkCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="分类")
    default_duration = models.PositiveIntegerField("默认预计耗时(分钟)", default=30)
    priority = models.PositiveSmallIntegerField("优先级", choices=Housework.PRIORITY_CHOICES, default=2)
    frequency = models.CharField("重复频率", max_length=10, choices=Housework.FREQUENCY_CHOICES, default='weekly')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "家务模板"
        verbose_name_plural = "家务模板"
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def create_housework(self, user, planned_date):
        """根据模板创建家务记录"""
        return Housework.objects.create(
            title=self.title,
            description=self.description,
            category=self.category,
            user=user,
            planned_date=planned_date,
            planned_duration=self.default_duration,
            priority=self.priority,
            frequency=self.frequency,
        )


# 初始化默认分类
def create_default_categories():
    """创建默认的家务分类"""
    default_categories = [
        {"name": "清洁卫生", "color": "#FF6B6B", "icon": "🧹", "description": "打扫、清洁相关家务"},
        {"name": "洗衣整理", "color": "#4ECDC4", "icon": "👕", "description": "洗衣、整理衣物"},
        {"name": "烹饪饮食", "color": "#FFA07A", "icon": "🍳", "description": "做饭、饮食准备"},
        {"name": "购物采买", "color": "#98D8C8", "icon": "🛒", "description": "日用品、食材采购"},
        {"name": "维修维护", "color": "#FFD93D", "icon": "🔧", "description": "家庭维修、设备维护"},
        {"name": "其他", "color": "#95E1D3", "icon": "📋", "description": "其他类型家务"},
    ]
    
    for cat_data in default_categories:
        HouseworkCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={
                "color": cat_data["color"],
                "icon": cat_data["icon"],
                "description": cat_data["description"],
            }
        )