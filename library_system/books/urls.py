from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),

    path('book_list/', views.book_list, name='book_list'),

    path('create/', views.book_create, name='book_create'),

    path('<int:pk>/', views.book_detail, name='book_detail'),

    path('<int:pk>/update/', views.book_update, name='book_update'),

    path('book/delete/', views.book_delete, name='book_delete'),

    path('manage/', views.manage_page, name='manage_page'),

    path('author/create/', views.author_create, name='author_create'),
    path('author/update/<int:pk>/', views.author_update, name='author_update'),
    path('author/delete/<int:pk>/', views.author_delete, name='author_delete'),

    path('category/create/', views.category_create, name='category_create'),
    path('category/update/<int:pk>/', views.category_update, name='category_update'),
    path('category/delete/<int:pk>/', views.category_delete, name='category_delete'),


    path('user_book_list/', views.user_book_list, name='user_book_list'),

]