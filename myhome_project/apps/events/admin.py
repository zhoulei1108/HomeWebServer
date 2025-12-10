from django.contrib import admin
from django.utils.html import format_html
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "event_type_display", 
        "date", 
        "time", 
        "week_order_display",
        "priority",
        "active",
        "active_status",
        "next_occurrence_display",
        "created_at"
    )
    list_filter = (
        "event_type", 
        "active", 
        "priority",
        "created_at"
    )
    search_fields = ("name", "description")
    list_editable = ("active", "priority")
    ordering = ("-priority", "-created_at")
    
    # 分面搜索
    date_hierarchy = "created_at"
    
    # 字段分组
    fieldsets = (
        ("基本信息", {
            "fields": ("name", "description", "event_type", "priority")
        }),
        ("时间设置", {
            "fields": ("date", "time"),
            "classes": ("collapse",)
        }),
        ("月度周末设置", {
            "fields": ("week_order",),
            "classes": ("collapse",),
            "description": "仅适用于'每月第N个周末'类型的事件"
        }),
        ("状态", {
            "fields": ("active",)
        }),
    )
    
    # 只读字段
    readonly_fields = ("created_at", "updated_at")
    
    def event_type_display(self, obj):
        """显示带图标的事件类型"""
        return obj.event_type_display_with_icon
    event_type_display.short_description = "事件类型"
    
    def active_status(self, obj):
        """显示启用状态"""
        if obj.active:
            return format_html('<span style="color: green;">✅ 启用</span>')
        else:
            return format_html('<span style="color: red;">❌ 禁用</span>')
    active_status.short_description = "状态"
    
    def week_order_display(self, obj):
        """显示周末顺序"""
        if obj.week_order:
            return f"第{obj.week_order}个周末"
        return "-"
    week_order_display.short_description = "周末顺序"
    
    def next_occurrence_display(self, obj):
        """显示下次发生时间"""
        return obj.next_occurrence_display
    next_occurrence_display.short_description = "下次发生"
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related()
    
    # 自定义操作
    actions = ["make_active", "make_inactive"]
    
    def make_active(self, request, queryset):
        """批量启用"""
        updated = queryset.update(active=True)
        self.message_user(request, f"已启用 {updated} 个事件。")
    make_active.short_description = "批量启用选中的事件"
    
    def make_inactive(self, request, queryset):
        """批量禁用"""
        updated = queryset.update(active=False)
        self.message_user(request, f"已禁用 {updated} 个事件。")
    make_inactive.short_description = "批量禁用选中的事件"
