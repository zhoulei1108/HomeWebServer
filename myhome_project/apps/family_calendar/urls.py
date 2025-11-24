from django.urls import path
from . import views

app_name = "family_calendar"

urlpatterns = [
    # 日历视图
    path("", views.month_view, name="month_view"),
    path("<int:year>/<int:month>/", views.month_view, name="month_view_date"),
    path("day/<int:year>/<int:month>/<int:day>/", views.day_view, name="day_view"),
]