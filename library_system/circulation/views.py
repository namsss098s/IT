from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import BorrowTransaction
from .services import (
    add_book_to_ticket,
    remove_book_from_ticket,
    confirm_ticket,
    return_ticket,
    get_or_create_pending_ticket
)





# =========================
# TICKET MANAGEMENT (MAIN DASHBOARD)
# =========================
@login_required
def ticket_management_view(request):
    ticket = get_or_create_pending_ticket(request.user)

    return render(request, 'ticket_management.html', {
        'ticket': ticket
    })


@login_required
def add_to_ticket_view(request, edition_id):

    if request.method != "GET":
        return redirect('ticket_management')

    result = add_book_to_ticket(
        user=request.user,
        edition_id=edition_id
    )

    if not result["success"]:
        ticket = get_or_create_pending_ticket(request.user)
        return render(request, 'ticket_management.html', {
            'error': result["message"],
            'ticket': ticket
        })

    return redirect('ticket_management')

@login_required
def remove_from_ticket_view(request, edition_id):

    if request.method != "GET":
        return redirect('ticket_management')

    result = remove_book_from_ticket(
        user=request.user,
        edition_id=edition_id
    )

    if not result["success"]:
        ticket = get_or_create_pending_ticket(request.user)
        return render(request, 'ticket_management.html', {
            'error': result["message"],
            'ticket': ticket
        })

    return redirect('ticket_management')

@login_required
def confirm_ticket_view(request):

    if request.method != "GET":
        return redirect('ticket_management')

    result = confirm_ticket(user=request.user)

    if not result["success"]:
        ticket = get_or_create_pending_ticket(request.user)
        return render(request, 'ticket_management.html', {
            'error': result["message"],
            'ticket': ticket
        })

    return redirect('ticket_management')

@login_required
def return_ticket_view(request, pk):

    result = return_ticket(
        ticket_id=pk,
        staff_user=request.user
    )

    if not result["success"]:
        return redirect('borrow_history')

    return redirect('borrow_history')

@login_required
def borrow_history_view(request):

    tickets = BorrowTransaction.objects.filter(
        status__in=['BORROWED', 'RETURNED', 'OVERDUE']
    ).select_related(
        'edition__book',
        'member',
        'staff'
    ).order_by('-borrow_date')

    return render(request, 'borrow_history.html', {
        'tickets': tickets
    })

