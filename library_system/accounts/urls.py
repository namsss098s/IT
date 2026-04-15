from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect_dashboard'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('check-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/update/<int:pk>/', views.member_update, name='member_update'),
    path('members/delete/<int:pk>/', views.member_delete, name='member_delete'),
    path('members/<int:pk>/json/', views.member_json, name='member_json'),
    path('profile/', views.profile_view, name='profile'),
]