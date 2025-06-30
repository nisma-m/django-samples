from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Book, Author, Borrower , PDFBook , DownloadLog
from .forms import BookForm, BorrowerForm,PDFBookForm ,SimpleUserCreationForm
from datetime import date , timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
import os


# 📚 Book List - shows only available books
@login_required
def book_list(request):
    books = Book.objects.select_related('author').all()
    authors = Author.objects.all()
    genres = Book.objects.values_list('genre', flat=True).distinct()

    author_id = request.GET.get('author')
    genre = request.GET.get('genre')

    # Filter books based on author and genre
    if author_id:
        books = books.filter(author_id=author_id)
    if genre:
        books = books.filter(genre__iexact=genre)

    # Exclude books that are currently borrowed (return_date is null)
    borrowed_books = Borrower.objects.filter(return_date__isnull=True).values_list('book_id', flat=True)
    books = books.exclude(id__in=borrowed_books)

    return render(request, 'book_list.html', {
        'books': books,
        'authors': authors,
        'genres': genres,
    })


# ➕ Add Book
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


# ✏️ Edit Book
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


# 🗑️ Delete Book
# def book_delete(request, pk):
#     book = get_object_or_404(Book, pk=pk)
#     if request.method == 'POST':
#         book.delete()
#         return redirect('book_list')
#     return render(request, 'book_confirm_delete.html', {'book': book})
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'confirm_delete.html', {
        'object': book,
        'cancel_url': reverse('book_list')
    })


# 👤 Author Detail Page
def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'author_detail.html', {'author': author})


# 📚 Borrow Book
def borrow_book(request):
    form = BorrowerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('borrower_list')
    return render(request, 'borrow_form.html', {'form': form})


# 📋 List Borrowers
def borrower_list(request):
    borrowers = Borrower.objects.all()

    # Filtering logic
    book_id = request.GET.get('book')
    borrower_name = request.GET.get('name')
    only_active = request.GET.get('active')

    if book_id:
        borrowers = borrowers.filter(book_id=book_id)
    if borrower_name:
        borrowers = borrowers.filter(name__icontains=borrower_name)
    if only_active:
        borrowers = borrowers.filter(return_date__isnull=True)

    books = Book.objects.all()
    return render(request, 'borrow_list.html', {
        'borrowers': borrowers,
        'books': books
    })


# ✅ Mark Borrowed Book as Returned
def mark_returned(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)
    borrower.return_date = date.today()  # Automatically set return date here
    borrower.save()
    return redirect('borrower_list')

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFBookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pdf_list')
    else:
        form = PDFBookForm()
    return render(request, 'pdf_upload.html', {'form': form})


def pdf_list(request):
    query = request.GET.get('q')
    pdfs = PDFBook.objects.all()

    if query:
        pdfs = pdfs.filter(title__icontains=query) | pdfs.filter(author__icontains=query)

    return render(request, 'pdf_list.html', {'pdfs': pdfs})

def pdf_delete(request, pk):
    pdf = get_object_or_404(PDFBook, pk=pk)
    if request.method == 'POST':
        pdf.pdf_file.delete()
        pdf.delete()
        return redirect('pdf_list')
    return render(request, 'confirm_delete.html', {
        'object': pdf,
        'cancel_url': reverse('pdf_list')
    })



def get_client_ip(request):
    # Safely extract user's IP address
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


@login_required
def download_pdf(request, pk):
    pdf = get_object_or_404(PDFBook, pk=pk)

    # Limit: 3 downloads per day
    today = now().date()
    downloads_today = DownloadLog.objects.filter(
        user=request.user,
        timestamp__date=today
    ).count()

    if downloads_today >= 3:
        messages.error(request, "🚫 You’ve reached your daily limit of 3 downloads.")
        return redirect('pdf_list')

    # Log download
    DownloadLog.objects.create(
        user=request.user,
        pdf=pdf,
        ip_address=get_client_ip(request)
    )

    # Force download with proper headers
    file_path = pdf.pdf_file.path
    if not os.path.exists(file_path):
        raise Http404("File not found.")

    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(file_path)
    )



@login_required
def dashboard(request):
    top_pdfs = DownloadLog.objects.values('pdf__title').annotate(
        total=Count('pdf')
    ).order_by('-total')[:5]

    # Calculate max to avoid division in template
    max_downloads = top_pdfs[0]['total'] if top_pdfs else 1

    # Precompute percentages
    for pdf in top_pdfs:
        pdf['percent'] = round((pdf['total'] / max_downloads) * 100)

    return render(request, 'dashboard.html', {
        'top_pdfs': top_pdfs
    })

def signup_view(request):
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')
    else:
        form = SimpleUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})