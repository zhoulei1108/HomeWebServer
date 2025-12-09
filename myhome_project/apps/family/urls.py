from django.urls import path
from . import views

app_name = 'family'

urlpatterns = [
    # 家庭仪表板和主要功能
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_family, name='create'),
    path('search/', views.search_family, name='search'),
    path('switch/<int:family_id>/', views.switch_family, name='switch'),
    
    # 邀请管理
    path('invitations/', views.invitations, name='invitations'),
    path('invitations/<int:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitations/<int:invitation_id>/reject/', views.reject_invitation, name='reject_invitation'),
    path('send-invitation/', views.send_invitation, name='send_invitation'),
    path('join-by-code/', views.join_by_code, name='join_by_code'),
    
    # 个人资料
    path('profile/', views.profile_view, name='profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/<int:user_id>/', views.profile_public, name='profile_public'),
]