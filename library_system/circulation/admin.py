from django.contrib import admin
from .models import BorrowRule, FineRule, BorrowTransaction

admin.site.register(BorrowRule)
admin.site.register(FineRule)
admin.site.register(BorrowTransaction)