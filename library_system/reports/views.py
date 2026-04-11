from django.shortcuts import render
from books.models import Book
from circulation.models import BorrowTransaction
from django.utils import timezone
from django.contrib.auth.models import User


def report_dashboard(request):
    total_books = Book.objects.count()
    total_members = User.objects.count()
    total_borrowed = BorrowTransaction.objects.filter(status='borrowed').count()
    total_overdue = BorrowTransaction.objects.filter(status='overdue').count()

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'total_borrowed': total_borrowed,
        'total_overdue': total_overdue,
    }

    return render(request, 'reports/dashboard.html', context)


def overdue_report(request):
    overdue = BorrowTransaction.objects.filter(status='overdue')

    return render(request, 'reports/overdue.html', {
        'transactions': overdue
    })


def borrow_report(request):
    transactions = BorrowTransaction.objects.all().order_by('-borrow_date')

    return render(request, 'reports/borrow_report.html', {
        'transactions': transactions
    })