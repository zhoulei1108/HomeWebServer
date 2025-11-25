from django.urls import path
from . import views

app_name = 'housework'

urlpatterns = [
    # 家务管理
    path('', views.housework_list, name='list'),
    path('create/', views.create_housework, name='create'),
    path('<int:pk>/', views.housework_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_housework, name='edit'),
    path('<int:pk>/complete/', views.complete_housework, name='complete'),
    path('<int:pk>/delete/', views.delete_housework, name='delete'),
    
    # 统计
    path('statistics/', views.statistics_view, name='statistics'),
    
    # AJAX接口
    path('api/month/', views.get_month_houseworks, name='month_data'),
    
    # 模板管理
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.create_template, name='create_template'),
]