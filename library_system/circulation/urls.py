from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    # =========================
    # TICKET MANAGEMENT
    # =========================
    path('tickets/', views.ticket_management_view, name='ticket_management'),

    path('tickets/add/<int:edition_id>/', views.add_to_ticket_view, name='ticket_add'),
    path('tickets/remove/<int:edition_id>/', views.remove_from_ticket_view, name='ticket_remove'),
    path('tickets/confirm/<int:ticket_id>/', views.confirm_ticket_view, name='ticket_confirm'),

    # ✅ NEW
    path('tickets/approve/<int:ticket_id>/', views.approve_ticket_view, name='ticket_approve'),

    # =========================
    # BORROW HISTORY
    # =========================
    path('borrow-history/', views.borrow_history_view, name='borrow_history'),

    # =========================
    # RETURN BOOK
    # =========================
    path('return/<int:pk>/', views.return_ticket_view, name='return_ticket'),

    path('my-books/', views.my_books_view, name='my_books'),
    path('rules/', views.rules_view, name='rules'),
]