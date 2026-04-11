from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Edition
from .forms import BookForm


def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    editions = Edition.objects.filter(book=book)

    return render(request, 'books/book_detail.html', {
        'book': book,
        'editions': editions
    })


def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()

            # OPTIONAL: nếu em muốn tạo edition mặc định
            Edition.objects.create(
                book=book,
                edition_number=1,
                quantity=0
            )

            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'books/book_form.html', {'form': form})


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(request, 'books/book_form.html', {'form': form})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('book_list')