from django.contrib import admin
from .models import BorrowRule, FineRule, BorrowTransaction, BorrowTransactionItem



@admin.register(BorrowRule)
class BorrowRuleAdmin(admin.ModelAdmin):
    list_display = ('description', 'max_days', 'max_books')


@admin.register(FineRule)
class FineRuleAdmin(admin.ModelAdmin):
    list_display = ('description', 'fine_per_day')



class BorrowTransactionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
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
        'items__edition__book__title',
        'staff__username',
    )

    readonly_fields = (
        'borrow_date',
        'fine_amount',
    )

    ordering = ('-id',)


class BorrowTransactionItemInline(admin.TabularInline):
    model = BorrowTransactionItem
    extra = 0


BorrowTransactionAdmin.inlines = [BorrowTransactionItemInline]
admin.site.register(BorrowTransaction, BorrowTransactionAdmin)
