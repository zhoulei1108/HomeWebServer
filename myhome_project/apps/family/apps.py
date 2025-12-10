from django.apps import AppConfig


class FamilyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.family'
    verbose_name = '家庭管理'
    
    def ready(self):
        """应用启动时的初始化"""
        import apps.family.signals  # noqa