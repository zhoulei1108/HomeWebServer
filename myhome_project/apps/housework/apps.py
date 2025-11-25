from django.apps import AppConfig


class HouseworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.housework'
    verbose_name = '家务管理'
    
    def ready(self):
        """应用启动时初始化数据"""
        from .models import create_default_categories
        # 创建默认分类
        # create_default_categories()  # 注释掉，避免重复创建