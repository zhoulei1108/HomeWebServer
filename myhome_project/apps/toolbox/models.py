from django.db import models
from django.contrib.auth.models import User


class LinkCategory(models.Model):
    """链接分类"""
    name = models.CharField('分类名称', max_length=50)
    icon = models.CharField('图标', max_length=50, default='fas fa-folder')
    color = models.CharField('颜色', max_length=7, default='#6c757d', 
                           help_text='HEX颜色代码，如：#FF6B6B')
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '链接分类'
        verbose_name_plural = '链接分类'
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class CustomLink(models.Model):
    """自定义链接"""
    title = models.CharField('标题', max_length=100)
    url = models.URLField('链接地址')
    description = models.TextField('描述', max_length=200, blank=True)
    category = models.ForeignKey(LinkCategory, verbose_name='分类', 
                               on_delete=models.CASCADE, related_name='links')
    icon = models.CharField('图标', max_length=50, default='fas fa-link')
    is_new_tab = models.BooleanField('在新标签页打开', default=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, verbose_name='创建人', 
                                 on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = '自定义链接'
        verbose_name_plural = '自定义链接'
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title
