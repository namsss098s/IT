from django.utils import timezone
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
    ticket = BorrowTransaction.objects.select_related('member').prefetch_related('items__edition').filter(
        member=user,
        status='PENDING'
    ).first()

    if not ticket:
        return {"success": False, "message": "No pending ticket"}

    items = ticket.items.all()
    if not items.exists():
        return {"success": False, "message": "Ticket is empty"}

    rule = BorrowRule.objects.first()
    borrow_days = rule.max_days if rule else 7

    active_borrows = BorrowTransaction.objects.filter(
        member=user,
        status='BORROWED'
    ).count()

    if rule and active_borrows + items.count() > rule.max_books:
        return {"success": False, "message": "Max borrow limit reached"}

    # 🔥 VALIDATE STOCK FIRST (IMPORTANT FIX)
    for item in items:
        if item.edition.available_quantity < item.quantity:
            return {"success": False, "message": f"Not enough stock for {item.edition.book.title}"}

    # update ticket AFTER validation
    ticket.status = 'BORROWED'
    ticket.due_date = timezone.now() + timedelta(days=borrow_days)
    ticket.save()

    # reduce stock safely
    for item in items:
        edition = item.edition
        edition.available_quantity -= item.quantity
        edition.save()

    return {"success": True, "ticket": ticket}

def return_ticket(*, ticket_id, staff_user=None):
    ticket = BorrowTransaction.objects.prefetch_related('items__edition').get(id=ticket_id)

    if ticket.status not in ['BORROWED', 'OVERDUE']:
        return {"success": False, "message": "Invalid ticket"}

    ticket.return_date = timezone.now()
    ticket.staff = staff_user

    fine_rule = FineRule.objects.first()
    now = timezone.now()

    if ticket.due_date and now > ticket.due_date:
        ticket.status = 'OVERDUE'

        if fine_rule:
            days = (now.date() - ticket.due_date.date()).days
            ticket.fine_amount = Decimal(days) * fine_rule.fine_per_day
    else:
        ticket.status = 'RETURNED'

    ticket.save()

    # restore stock
    for item in ticket.items.all():
        edition = item.edition
        edition.available_quantity += item.quantity
        edition.save()

    return {"success": True, "ticket": ticket}

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
    