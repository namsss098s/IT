from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from books.models import Book
from circulation.models import BorrowTransaction
from django.utils import timezone
from django.contrib.auth.models import User


def can_view_reports(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return getattr(getattr(user, 'staffprofile', None), 'role', None) in ['admin', 'librarian']


@login_required
@user_passes_test(can_view_reports)
def report_dashboard(request):
    total_books = Book.objects.count()
    total_members = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_borrowed = BorrowTransaction.objects.filter(status='BORROWED').count()
    total_overdue = BorrowTransaction.objects.filter(status='OVERDUE').count()

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'total_borrowed': total_borrowed,
        'total_overdue': total_overdue,
    }

    return render(request, 'reports/dashboard.html', context)


@login_required
@user_passes_test(can_view_reports)
def overdue_report(request):
    overdue = BorrowTransaction.objects.filter(status='OVERDUE')

    return render(request, 'reports/overdue.html', {
        'transactions': overdue
    })


@login_required
@user_passes_test(can_view_reports)
def borrow_report(request):
    transactions = BorrowTransaction.objects.all().order_by('-borrow_date')

    return render(request, 'reports/borrow_report.html', {
        'transactions': transactions
    })
