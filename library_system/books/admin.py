from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Book,
    Category,
    Author,
    Edition
)


# 🔥 Edition inline
class EditionInline(admin.TabularInline):

    model = Edition

    extra = 1

    fields = (
        'edition_number',
        'quantity',
        'available_quantity',
    )

    readonly_fields = (
        'available_quantity',
    )


# 📚 Book admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        'cover_preview',
        'title',
        'category',
        'publisher',
        'price',
        'total_stock',
    )

    search_fields = (
        'title',
        'publisher',
    )

    list_filter = (
        'category',
    )

    filter_horizontal = (
        'authors',
    )

    inlines = [EditionInline]

    # 🔥 total available books
    def total_stock(self, obj):
        return sum(
            ed.available_quantity
            for ed in obj.editions.all()
        )

    total_stock.short_description = 'Available'

    # 🔥 image preview
    def cover_preview(self, obj):

        if obj.cover:
            return format_html(
                '<img src="{}" width="50" height="70" style="object-fit:cover;border-radius:4px;" />',
                obj.cover.url
            )

        return "No Cover"

    cover_preview.short_description = 'Cover'


# 📂 Category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    search_fields = (
        'name',
    )


# ✍️ Author admin
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    search_fields = (
        'name',
    )


# 📦 Edition admin
@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):

    list_display = (
        'book',
        'edition_number',
        'quantity',
        'available_quantity',
    )

    list_filter = (
        'book',
    )