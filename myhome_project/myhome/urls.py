"""
URL configuration for myhome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path, include, reverse_lazy

from apps.family_calendar import views as calendar_views
from apps.family import views as family_views

urlpatterns = [
    # 根路径重定向到家庭仪表板（如果没有家庭则显示引导）
    path("", lambda request: redirect('family:dashboard'), name="home"),
    path("admin/", admin.site.urls),
    # 手动配置认证URL
    path("accounts/", lambda request: redirect('login'), name="accounts"),
    path(
        "accounts/login/",
        family_views.login_view,
        name="login",
    ),
    path("accounts/logout/", calendar_views.logout_view, name="logout"),
    path("accounts/register/", calendar_views.register, name="register"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("accounts/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("family/", include("apps.family.urls")),
    path("calendar/", include("apps.family_calendar.urls")),
    path("events/", include("apps.events.urls")),
    path("housework/", include("apps.housework.urls")),
    path("toolbox/", include("apps.toolbox.urls")),
]
