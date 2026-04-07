from django.urls import path
from . import views

urlpatterns = [
    path('', views.borrow_list, name='borrow_list'),
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
]