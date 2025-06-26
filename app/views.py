from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Author
from .forms import BookForm
from django.db.models import Q


def book_list(request):
    books = Book.objects.select_related('author').all()
    authors = Author.objects.all()
    genres = Book.objects.values_list('genre', flat=True).distinct()

    author_id = request.GET.get('author')
    genre = request.GET.get('genre')

    if author_id:
        books = books.filter(author_id=author_id)

    if genre:
        books = books.filter(genre__iexact=genre)  # case-insensitive exact match

    return render(request, 'book_list.html', {
        'books': books,
        'authors': authors,
        'genres': genres,
    })


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'author_detail.html', {'author': author})
