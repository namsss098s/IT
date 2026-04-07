from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import BorrowTransaction, FineRule
from .forms import BorrowForm


def borrow_list(request):
    transactions = BorrowTransaction.objects.all().order_by('-borrow_date')
    return render(request, 'circulation/borrow_list.html', {'transactions': transactions})


def borrow_book(request):
    form = BorrowForm(request.POST or None)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.staff = request.user
        transaction.status = 'borrowed'
        transaction.save()
        return redirect('borrow_list')

    return render(request, 'circulation/borrow_form.html', {'form': form})


def return_book(request, pk):
    transaction = get_object_or_404(BorrowTransaction, pk=pk)

    transaction.return_date = timezone.now()
    transaction.status = 'returned'

    # calculate fine
    if transaction.return_date > transaction.due_date:
        days_overdue = (transaction.return_date - transaction.due_date).days
        fine_rule = FineRule.objects.first()
        if fine_rule:
            transaction.fine_amount = days_overdue * fine_rule.fine_per_day

    transaction.save()

    return redirect('borrow_list')


def mark_overdue():
    transactions = BorrowTransaction.objects.filter(status='borrowed')
    now = timezone.now()

    for t in transactions:
        if now > t.due_date:
            t.status = 'overdue'
            t.save()