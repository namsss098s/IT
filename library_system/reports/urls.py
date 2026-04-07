from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('overdue/', views.overdue_report, name='overdue_report'),
    path('borrow/', views.borrow_report, name='borrow_report'),
]