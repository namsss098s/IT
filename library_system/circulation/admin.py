from django.contrib import admin
from .models import BorrowRule, FineRule, BorrowTransaction



@admin.register(BorrowRule)
class BorrowRuleAdmin(admin.ModelAdmin):
    list_display = ('description', 'max_days', 'max_books')


@admin.register(FineRule)
class FineRuleAdmin(admin.ModelAdmin):
    list_display = ('description', 'fine_per_day')



class BorrowTransactionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'edition',
        'member',
        'status',
        'borrow_date',
        'due_date',
        'return_date',
        'fine_amount',
        'staff',
    )

    list_filter = (
        'status',
        'borrow_date',
        'due_date',
        'staff',
    )

    search_fields = (
        'member__username',
        'member__email',
        'edition__book__title',
        'staff__username',
    )

    readonly_fields = (
        'borrow_date',
        'fine_amount',
        'reject_reason',
    )

    ordering = ('-id',)