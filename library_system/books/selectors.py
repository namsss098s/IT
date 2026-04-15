from django.db.models import Q, Sum
from .models import Book, Edition


# 📚 Lấy tất cả books (optimize)
def get_all_books():
    return Book.objects.select_related('category') \
        .prefetch_related('authors', 'editions')


# 🔍 Search book (title + author)
def search_books(query):
    return Book.objects.filter(
        Q(title__icontains=query) |
        Q(authors__name__icontains=query)
    ).select_related('category') \
     .prefetch_related('authors', 'editions') \
     .distinct()


# 📖 Lấy chi tiết book (full data)
def get_book_detail(book_id):
    return Book.objects.select_related('category') \
        .prefetch_related('authors', 'editions') \
        .get(id=book_id)


# 📦 Lấy tất cả edition của 1 book
def get_book_editions(book_id):
    return Edition.objects.filter(book_id=book_id)


# ✅ Lấy edition còn sách (dùng cho borrow)
def get_available_editions(book_id):
    return Edition.objects.filter(
        book_id=book_id,
        available_quantity__gt=0
    )


# 🔎 Lấy 1 edition
def get_edition_by_id(edition_id):
    return Edition.objects.get(id=edition_id)


# 📊 Tổng số sách còn lại của 1 book
def get_total_available_books(book_id):
    return Edition.objects.filter(book_id=book_id) \
        .aggregate(total=Sum('available_quantity'))['total'] or 0


# 📊 Tổng số sách (kho)
def get_total_quantity_books(book_id):
    return Edition.objects.filter(book_id=book_id) \
        .aggregate(total=Sum('quantity'))['total'] or 0


# 📚 Lọc theo category
def get_books_by_category(category_id):
    return Book.objects.filter(category_id=category_id) \
        .select_related('category') \
        .prefetch_related('authors', 'editions')


# 🧑‍💻 Lấy book theo author
def get_books_by_author(author_id):
    return Book.objects.filter(authors__id=author_id) \
        .select_related('category') \
        .prefetch_related('authors', 'editions') \
        .distinct()