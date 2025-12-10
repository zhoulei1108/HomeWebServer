from django.contrib import admin
from django.utils.html import format_html
from .models import Housework, HouseworkCategory, HouseworkTemplate


@admin.register(HouseworkCategory)
class HouseworkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color_display', 'description']
    search_fields = ['name']
    list_editable = ['icon']
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = '颜色'


@admin.register(HouseworkTemplate)
class HouseworkTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'default_duration', 'priority', 'frequency', 'created_by']
    list_filter = ['category', 'priority', 'frequency', 'created_by']
    search_fields = ['title', 'description']
    list_editable = ['category', 'default_duration', 'priority', 'frequency']


@admin.register(Housework)
class HouseworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'planned_date', 'status', 'priority', 'duration_info']
    list_filter = ['status', 'priority', 'category', 'user', 'frequency', 'planned_date']
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority']
    date_hierarchy = 'planned_date'
    ordering = ['-planned_date', '-priority']
    
    def duration_info(self, obj):
        if obj.actual_duration:
            diff = obj.actual_duration - obj.planned_duration
            if diff > 0:
                return format_html('{} 分钟 (+{})', obj.actual_duration, diff)
            elif diff < 0:
                return format_html('{} 分钟 ({})', obj.actual_duration, diff)
            else:
                return f'{obj.actual_duration} 分钟'
        return f'{obj.planned_duration} 分钟'
    duration_info.short_description = '耗时信息'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'category', 'user')
        }),
        ('时间安排', {
            'fields': ('planned_date', 'planned_duration', 'actual_duration', 'frequency')
        }),
        ('状态管理', {
            'fields': ('status', 'priority', 'completed_at')
        }),
    )
    
    readonly_fields = ['completed_at']