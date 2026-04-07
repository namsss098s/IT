from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('create/', views.member_create, name='member_create'),
    path('update/<int:pk>/', views.member_update, name='member_update'),
    path('delete/<int:pk>/', views.member_delete, name='member_delete'),
]