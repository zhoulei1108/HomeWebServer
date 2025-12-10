from django.contrib import admin
from .models import LinkCategory, CustomLink


@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'order', 'is_active', 'links_count']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order']
    
    def links_count(self, obj):
        return obj.links.filter(is_active=True).count()
    links_count.short_description = '链接数量'


@admin.register(CustomLink)
class CustomLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'category', 'icon', 'order', 'is_active', 'is_new_tab']
    list_editable = ['order', 'is_active']
    list_filter = ['category', 'is_active', 'is_new_tab', 'created_at']
    search_fields = ['title', 'url', 'description']
    ordering = ['category__order', 'order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')
