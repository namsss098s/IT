from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from books.models import Edition


class BorrowRule(models.Model):
    description = models.TextField()
    max_days = models.PositiveIntegerField(default=7)
    max_books = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.description


class FineRule(models.Model):
    description = models.TextField()
    fine_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.description


class BorrowTransaction(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('BORROWED', 'Borrowed'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
    )

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
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    # =========================
    # BUSINESS LOGIC
    # =========================

    def is_overdue(self):
        return (
            self.status == 'BORROWED'
            and self.due_date
            and timezone.now() > self.due_date
        )

    def calculate_fine(self, fine_per_day):
        if not self.is_overdue():
            return Decimal('0')

        days = (timezone.now().date() - self.due_date.date()).days
        return Decimal(days) * Decimal(str(fine_per_day))

    def mark_overdue(self):
        if self.is_overdue():
            self.status = 'OVERDUE'
            self.save()

    def __str__(self):
        return f"Transaction #{self.id} - {self.member.username}"
    
class BorrowTransactionItem(models.Model):

    transaction = models.ForeignKey(
        BorrowTransaction,
        on_delete=models.CASCADE,
        related_name='items'
    )

    edition = models.ForeignKey(
        Edition,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.edition.book.title}"