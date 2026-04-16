from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import BorrowRule, BorrowTransaction, FineRule
from .services import (
    add_book_to_ticket,
    approve_return_ticket,
    is_librarian,
    remove_book_from_ticket,
    confirm_ticket,
    get_or_create_pending_ticket
)





# =========================
# TICKET MANAGEMENT (MAIN DASHBOARD)
# =========================
@login_required
def ticket_management_view(request):

    if request.user.is_staff or request.user.is_superuser:
        tickets = BorrowTransaction.objects.prefetch_related(
            'items__edition__book'
        ).order_by('-id')
    else:
        tickets = BorrowTransaction.objects.filter(
            member=request.user
        ).prefetch_related(
            'items__edition__book'
        ).order_by('-id')

    return render(request, 'ticket_management.html', {
        'tickets': tickets
    })

@login_required
def add_to_ticket_view(request, edition_id):

    if request.method != "GET":
        return redirect('circulation:ticket_management')

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

    # 🎯 SUCCESS MESSAGE
    messages.success(
        request,
        "Đã thêm sách vào phiếu mượn"
    )

    if is_librarian(request.user):
        return redirect('circulation:ticket_management')
    else:
        return redirect('user_book_list')
    

@login_required
def remove_from_ticket_view(request, edition_id):

    if request.method != "GET":
        return redirect('circulation:ticket_management')

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

    # 🎯 phân flow theo role
    if is_librarian(request.user):
        return redirect('circulation:ticket_management')
    else:
        return redirect('circulation:my_books')

@login_required
def confirm_ticket_view(request, ticket_id):

    if request.method != "POST":
        return redirect('circulation:ticket_management')

    result = confirm_ticket(
        ticket_id=ticket_id,
        user=request.user
    )

    if not result["success"]:
        messages.error(request, result["message"])
    else:
        messages.success(request, "Ticket confirmed successfully")

    return redirect('circulation:ticket_management')

@login_required
def return_ticket_view(request, pk):

    if request.method != "POST":
        return redirect('circulation:my_books')

    ticket = get_object_or_404(BorrowTransaction, id=pk)

    # =========================
    # 👤 USER REQUEST RETURN
    # =========================
    if not is_librarian(request.user):

        if ticket.member != request.user:
            return HttpResponseForbidden("Not allowed")

        if ticket.status not in ["BORROWED", "OVERDUE"]:
            return redirect('circulation:my_books')

        ticket.status = "RETURN_REQUESTED"
        ticket.save()

        messages.success(request, "Return requested")

        return redirect('circulation:my_books')

    # =========================
    # 👨‍💼 ADMIN APPROVE RETURN
    # =========================
    result = approve_return_ticket(
        ticket_id=ticket.id,
        staff_user=request.user
    )

    if not result["success"]:
        messages.error(request, result["message"])
    else:
        messages.success(request, "Return approved successfully")

    return redirect('circulation:ticket_management')

@login_required
def borrow_history_view(request):

    borrows = BorrowTransaction.objects.filter(
        member=request.user
    ).select_related(
        'member', 'staff'
    ).prefetch_related(
        'items__edition__book'
    ).order_by('-id')

    return render(request, 'borrow_history.html', {
        'borrows': borrows
    })
@login_required
def my_books_view(request):
    borrows = (
        BorrowTransaction.objects
        .filter(
            member=request.user,
            status__in=['PENDING', 'BORROWED', 'OVERDUE']
        )
        .prefetch_related('items__edition__book')
    )

    return render(request, 'my_book.html', {
        'borrows': borrows
    })


@login_required
def rules_view(request):
    borrow_rule = BorrowRule.objects.first()
    fine_rule = FineRule.objects.first()

    return render(request, 'rules.html', {
        'borrow_rule': borrow_rule,
        'fine_rule': fine_rule
    })

def update_overdue_tickets():
    now = timezone.now()

    BorrowTransaction.objects.filter(
        status='BORROWED',
        due_date__lt=now
    ).update(status='OVERDUE')

from .services import approve_ticket

@login_required
def approve_ticket_view(request, ticket_id):

    # ✅ check quyền
    if not is_librarian(request.user):
        return HttpResponseForbidden()

    # 🔥 FIX: dùng POST
    if request.method != "POST":
        return redirect('circulation:ticket_management')

    result = approve_ticket(
        ticket_id=ticket_id,
        staff_user=request.user
    )

    if not result["success"]:
        messages.error(request, result["message"])
    else:
        messages.success(request, "Borrow approved successfully")

    return redirect('circulation:ticket_management')