from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
from decimal import Decimal

from .models import BorrowTransaction, BorrowTransactionItem, BorrowRule, FineRule
from books.models import Edition


def get_or_create_pending_ticket(user):
    ticket, created = BorrowTransaction.objects.get_or_create(
        member=user,
        status='PENDING',
        defaults={
            "due_date": None
        }
    )
    return ticket

def add_book_to_ticket(*, user, edition_id):
    edition = Edition.objects.select_related('book').get(id=edition_id)

    if edition.available_quantity <= 0:
        return {"success": False, "message": "Book not available"}

    ticket = get_or_create_pending_ticket(user)

    item, created = BorrowTransactionItem.objects.get_or_create(
        transaction=ticket,
        edition=edition,
        defaults={"quantity": 1}
    )

    if not created:
        # check stock before increase
        if item.quantity + 1 > edition.available_quantity:
            return {"success": False, "message": "Not enough stock"}

        item.quantity += 1
        item.save()

    return {"success": True, "ticket": ticket}

def remove_book_from_ticket(*, user, edition_id):
    ticket = get_or_create_pending_ticket(user)

    item = BorrowTransactionItem.objects.filter(
        transaction=ticket,
        edition_id=edition_id
    ).first()

    if not item:
        return {"success": False, "message": "Item not found"}

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return {"success": True, "ticket": ticket}

def confirm_ticket(*, user):
    ticket = BorrowTransaction.objects.filter(
        member=user,
        status='PENDING'
    ).first()

    if not ticket:
        return {"success": False, "message": "No pending ticket"}

    items = ticket.items.all()
    if not items.exists():
        return {"success": False, "message": "Ticket is empty"}

    # chỉ validate, KHÔNG trừ stock
    for item in items:
        if item.edition.available_quantity < item.quantity:
            return {"success": False, "message": f"Not enough stock for {item.edition.book.title}"}

    # 🔥 CHỈ mark pending (request gửi admin)
    ticket.status = 'PENDING'
    ticket.save()

    return {"success": True, "ticket": ticket}

def request_return_ticket(*, ticket_id, user):
    ticket = BorrowTransaction.objects.get(id=ticket_id, member=user)

    if ticket.status != 'BORROWED':
        return {"success": False, "message": "Cannot request return"}

    ticket.status = 'RETURN_REQUESTED'
    ticket.save()

    return {"success": True, "ticket": ticket}

def approve_return_ticket(*, ticket_id, staff_user):
    ticket = BorrowTransaction.objects.prefetch_related(
        'items__edition'
    ).get(id=ticket_id)

    if ticket.status != 'RETURN_REQUESTED':
        return {"success": False, "message": "Invalid ticket status"}

    now = timezone.now()
    fine_rule = FineRule.objects.first()

    # =========================
    # SET RETURNED STATUS (LUÔN LUÔN)
    # =========================
    ticket.status = 'RETURNED'
    ticket.return_date = now
    ticket.staff = staff_user

    # =========================
    # CALCULATE FINE (NẾU TRỄ)
    # =========================
    if ticket.due_date and now > ticket.due_date:
        if fine_rule:
            days = (now.date() - ticket.due_date.date()).days
            ticket.fine_amount = Decimal(days) * fine_rule.fine_per_day
    else:
        ticket.fine_amount = 0

    ticket.save()

    # =========================
    # RESTORE STOCK
    # =========================
    for item in ticket.items.all():
        edition = item.edition
        edition.available_quantity += item.quantity
        edition.save()

    return {"success": True, "ticket": ticket}

def approve_ticket(*, ticket_id, staff_user):
    ticket = BorrowTransaction.objects.prefetch_related('items__edition').get(id=ticket_id)

    if ticket.status != 'PENDING':
        return {"success": False, "message": "Invalid status"}

    rule = BorrowRule.objects.first()
    borrow_days = rule.max_days if rule else 7

    # set BORROWED
    ticket.status = 'BORROWED'
    ticket.borrow_date = timezone.now()
    ticket.due_date = timezone.now() + timedelta(days=borrow_days)
    ticket.staff = staff_user
    ticket.save()

    # 🔥 TRỪ STOCK Ở ĐÂY (đúng chuẩn)
    for item in ticket.items.all():
        edition = item.edition
        edition.available_quantity -= item.quantity
        edition.save()

    return {"success": True}


def reject_ticket(*, ticket_id, staff_user):
    ticket = BorrowTransaction.objects.get(id=ticket_id)

    ticket.status = 'REJECTED'
    ticket.staff = staff_user
    ticket.save()

    return {"success": True}

def update_overdue_tickets():
    now = timezone.now()

    updated = BorrowTransaction.objects.filter(
        status='BORROWED',
        due_date__lt=now
    ).update(status='OVERDUE')

    return updated

def is_librarian(user):
    try:
        return user.staffprofile.role in ['admin', 'librarian']
    except:
        return False
    
def my_books_view(request):
    transactions = (
        BorrowTransaction.objects
        .prefetch_related('items__edition__book')
        .filter(member=request.user, status__in=['BORROWED', 'OVERDUE'])
        .order_by('-borrow_date')
    )

    return render(request, 'circulation/my_books.html', {
        'transactions': transactions
    })