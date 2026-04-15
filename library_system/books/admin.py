from django.contrib import admin
from .models import Book, Category, Author, Edition


# 🔥 Edition inline (QUAN TRỌNG)
class EditionInline(admin.TabularInline):
    model = Edition
    extra = 1

    fields = (
        'edition_number',
        'quantity',
        'available_quantity',
    )

    readonly_fields = ('available_quantity',)


# 📚 Book admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'publisher', 'price', 'total_stock')
    search_fields = ('title', 'publisher')
    list_filter = ('category',)
    filter_horizontal = ('authors',)

    inlines = [EditionInline]

    # 🔥 hiển thị tổng số sách còn
    def total_stock(self, obj):
        return sum(ed.available_quantity for ed in obj.editions.all())
    total_stock.short_description = 'Available'


# 📂 Category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# ✍️ Author admin
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# 📦 Edition admin (optional, vẫn nên có)
@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = (
        'book',
        'edition_number',
        'quantity',
        'available_quantity',
    )

    list_filter = ('book',)