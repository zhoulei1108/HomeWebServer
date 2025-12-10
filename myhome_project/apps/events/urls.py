from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # 创建事件
    path("new/", views.create_event, name="create"),
    path("new/success/", views.create_success, name="create_success"),
    
    # 事件详情和列表
    path("", views.event_list, name="list"),
    path("<int:pk>/", views.event_detail, name="event_detail"),
    
    # 即将到来的事件
    path("upcoming/", views.upcoming_events, name="upcoming"),
    
    # 事件状态切换
    path("<int:pk>/toggle/", views.toggle_event_status, name="toggle_status"),
    
    # 删除事件
    path("<int:pk>/delete/", views.delete_event, name="delete"),
]
