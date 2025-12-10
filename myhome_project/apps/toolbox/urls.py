from django.urls import path
from . import views

app_name = 'toolbox'

urlpatterns = [
    path('', views.toolbox_index, name='index'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('link/create/', views.link_create, name='link_create'),
    path('link/<int:pk>/edit/', views.link_edit, name='link_edit'),
    path('link/<int:pk>/delete/', views.link_delete, name='link_delete'),
]
