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
    path('tickets/confirm/', views.confirm_ticket_view, name='ticket_confirm'),

    # =========================
    # BORROW HISTORY
    # =========================
    path('borrow-history/', views.borrow_history_view, name='borrow_history'),

    # =========================
    # RETURN BOOK
    # =========================
    path('return/<int:pk>/', views.return_ticket_view, name='return_ticket'),
]