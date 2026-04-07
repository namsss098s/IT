from django.contrib import admin
from .models import Category, Author, Book, Edition

admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Edition)