import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Category, Author, Edition
from .forms import BookForm
from django.core.paginator import Paginator
from .selectors import (
    get_all_books,
    search_books,
    get_book_detail,
    get_book_editions,
    get_books_by_category
)
from .services import update_total_quantity


# ===== LIST =====
def book_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    books = Book.objects.all()

    if query:
        books = books.filter(title__icontains=query)

    if category_id:
        books = books.filter(category_id=category_id)

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    authors = Author.objects.all()

    return render(request, 'book_management.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_category': category_id,
        'categories': categories,
        'authors': authors
    })


# ===== DETAIL =====
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    editions = book.editions.all()

    return render(request, 'book_detail.html', {
        'book': book,
        'editions': editions
    })


# ===== CREATE =====
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            print("VALID OK")

            book = form.save(commit=False)
            book.save()
            form.save_m2m()

            Edition.objects.create(
                book=book,
                edition_number=int(request.POST.get("edition_number") or 1),
                quantity=int(request.POST.get("quantity") or 0)
            )

            return redirect('book_list')

        else:
            print("FORM ERROR:", form.errors)  # 🔥 THÊM DÒNG NÀY

    return redirect('book_list')


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)

        if form.is_valid():
            book = form.save(commit=False)
            book.save()

            # 🔥 QUAN TRỌNG
            form.save_m2m()

    return redirect('book_list')


# ===== DELETE =====
def book_delete(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")

        print("DELETE ID:", book_id)  # debug

        book = get_object_or_404(Book, id=book_id)
        book.delete()

    return redirect('book_list')
# ===== PAGE =====
def manage_page(request):
    authors = Author.objects.all()
    categories = Category.objects.all()

    return render(request, 'manage.html', {
        'authors': authors,
        'categories': categories
    })


# ===== AUTHOR =====
def author_create(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Author.objects.create(name=name)

    return redirect('manage_page')


def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            author.name = name
            author.save()

    return redirect('manage_page')


def author_delete(request, pk):
    if request.method == "POST":
        author = get_object_or_404(Author, pk=pk)
        author.delete()

    return redirect('manage_page')


# ===== CATEGORY =====
def category_create(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Category.objects.create(name=name)

    return redirect('manage_page')


def category_update(request, pk):
    cate = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            cate.name = name
            cate.save()

    return redirect('manage_page')


def category_delete(request, pk):
    if request.method == "POST":
        cate = get_object_or_404(Category, pk=pk)
        cate.delete()

    return redirect('manage_page')