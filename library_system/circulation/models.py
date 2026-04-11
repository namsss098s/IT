from django.db import models
from books.models import Book
from django.contrib.auth.models import User


class BorrowRule(models.Model):
    description = models.TextField()
    max_days = models.IntegerField()
    max_books = models.IntegerField()

    def __str__(self):
        return self.description


class FineRule(models.Model):
    description = models.TextField()
    fine_per_day = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.description


class BorrowTransaction(models.Model):

    STATUS_CHOICES = (
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrowed_transactions'
    )

    staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_transactions'
    )

    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.book} - {self.member}"