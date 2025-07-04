from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Book, Author, Borrower , PDFBook , DownloadLog
from .forms import BookForm, BorrowerForm,PDFBookForm ,SimpleUserCreationForm
from datetime import date , timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
import os
from django.contrib.auth import login
import PyPDF2
from io import BytesIO
from django.core.files.base import ContentFile
import requests
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from django.shortcuts import render
from datetime import timedelta
from django.utils.timezone import now
import fitz  # PyMuPDF
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from cloudinary.utils import cloudinary_url
from django.core.files.uploadedfile import SimpleUploadedFile
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload as cloudinary_upload
import re
from cloudinary.utils import cloudinary_url
import cloudinary.uploader
from django.contrib.auth.models import User




def is_librarian(user):
    return user.groups.filter(name='Librarian').exists()


# 📚 Book List - shows only available books
@login_required
def book_list(request):
    books = Book.objects.select_related('author').all()
    authors = Author.objects.all()
    genres = Book.objects.values_list('genre', flat=True).distinct()

    author_id = request.GET.get('author')
    genre = request.GET.get('genre')

    if author_id:
        books = books.filter(author_id=author_id)
    if genre:
        books = books.filter(genre__iexact=genre)

    # Get currently borrowed book IDs
    borrowed_books = Borrower.objects.filter(return_date__isnull=True).values_list('book_id', flat=True)

    # Mark availability for template display
    for book in books:
        book.is_available = book.id not in borrowed_books

    return render(request, 'book_list.html', {
        'books': books,
        'authors': authors,
        'genres': genres,
    })



# ➕ Add Book
@login_required
@user_passes_test(is_librarian)
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
@user_passes_test(is_librarian)
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
@user_passes_test(is_librarian)
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



@user_passes_test(is_librarian)
def upload_pdf(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        pdf_file = request.FILES.get('pdf_file')

        if not title or not author or not pdf_file:
            messages.error(request, "All fields are required.")
            return redirect('pdf_upload')

        try:
            result = cloudinary_upload(
                pdf_file,
                resource_type="raw",
                type="upload",
                folder="pdfs/",
                public_id=os.path.splitext(pdf_file.name)[0],
                overwrite=True
            )

            PDFBook.objects.create(
                title=title,
                author=author,
                pdf_file=result['secure_url']
            )
            messages.success(request, "✅ PDF uploaded successfully.")
            return redirect('pdf_list')

        except Exception as e:
            messages.error(request, f"Upload failed: {e}")
            return redirect('pdf_upload')

    return render(request, 'upload_pdf.html')




def pdf_list(request):
    query = request.GET.get('q')
    pdfs = PDFBook.objects.all()

    if query:
        pdfs = pdfs.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    return render(request, 'pdf_list.html', {'pdfs': pdfs})

def pdf_delete(request, pk):
    pdf = get_object_or_404(PDFBook, pk=pk)
    
    public_id = extract_public_id(pdf.pdf_file)
    if public_id:
        # Delete file from Cloudinary
        cloudinary.uploader.destroy(public_id, resource_type='raw')
    
    # Delete DB record
    pdf.delete()
    
    return redirect('pdf_list')  # or wherever




def get_client_ip(request):
    # Safely extract user's IP address
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

#this is give unlimited download access to librarian and limited for normal


@login_required
def download_pdf(request, pk):
    pdf = get_object_or_404(PDFBook, pk=pk)

    # Limit daily downloads for non-librarians
    if not is_librarian(request.user):
        today = now().date()
        downloads_today = DownloadLog.objects.filter(
            user=request.user,
            timestamp__date=today
        ).count()
        if downloads_today >= 3:
            messages.error(request, "🚫 Daily download limit (3) reached.")
            return redirect('pdf_list')

    # Log the download
    DownloadLog.objects.create(
        user=request.user,
        pdf=pdf,
        ip_address=get_client_ip(request)
    )

    # Fetch PDF content from Cloudinary
    try:
        response = requests.get(pdf.pdf_file, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        messages.error(request, "❌ Error downloading file from Cloudinary.")
        return redirect('pdf_list')

    filename = os.path.basename(pdf.pdf_file)
    return HttpResponse(
        response.content,
        content_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

# this gives limited download for both librarian and reader
# @login_required
# def download_pdf(request, pk):
#     pdf = get_object_or_404(PDFBook, pk=pk)

#     # Limit: 3 downloads per day
#     today = now().date()
#     downloads_today = DownloadLog.objects.filter(
#         user=request.user,
#         timestamp__date=today
#     ).count()

#     if downloads_today >= 3:
#         messages.error(request, "🚫 You’ve reached your daily limit of 3 downloads.")
#         return redirect('pdf_list')

#     # Log download
#     DownloadLog.objects.create(
#         user=request.user,
#         pdf=pdf,
#         ip_address=get_client_ip(request)
#     )

#     # Force download with proper headers
#     file_path = pdf.pdf_file.path
#     if not os.path.exists(file_path):
#         raise Http404("File not found.")

#     return FileResponse(
#         open(file_path, 'rb'),
#         as_attachment=True,
#         filename=os.path.basename(file_path)
#     )





@login_required
@user_passes_test(lambda u: u.groups.filter(name="Librarian").exists())
def dashboard(request):
    logs = DownloadLog.objects.all()

    user_id = request.GET.get("user")
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")
    selected_user = None

    if user_id:
        logs = logs.filter(user_id=user_id)
        try:
            selected_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            selected_user = None

    if start_date and end_date:
        logs = logs.filter(timestamp__date__range=[start_date, end_date])

    # Daily Downloads
    daily_downloads = logs.annotate(
        date=TruncDate("timestamp")
    ).values("date").annotate(
        count=Count("id")
    ).order_by("date")

    # Weekly Downloads (last 7 days)
    last_7_days = now().date() - timedelta(days=6)
    weekly_data = logs.filter(
        timestamp__date__gte=last_7_days
    ).annotate(
        date=TruncDate("timestamp")
    ).values("date").annotate(
        count=Count("id")
    ).order_by("date")

    # Top 3 PDFs
    if user_id:
        top_pdfs = logs.values("pdf__title").annotate(
            count=Count("id")
        ).order_by("-count")[:3]
    else:
        top_pdfs = DownloadLog.objects.values("pdf__title").annotate(
            count=Count("id")
        ).order_by("-count")[:3]

    top_titles = [item["pdf__title"] for item in top_pdfs]
    top_counts = [item["count"] for item in top_pdfs]


    # Prepare chart data
    daily_labels = [str(item["date"]) for item in daily_downloads]
    daily_counts = [item["count"] for item in daily_downloads]

    weekly_labels = [str(item["date"]) for item in weekly_data]
    weekly_counts = [item["count"] for item in weekly_data]

    top_titles = [item["pdf__title"] for item in top_pdfs]
    top_counts = [item["count"] for item in top_pdfs]

    return render(request, "dashboard.html", {
        "daily_labels": daily_labels,
        "daily_counts": daily_counts,
        "weekly_labels": weekly_labels,
        "weekly_counts": weekly_counts,
        "top_titles": top_titles,
        "top_counts": top_counts,
        "users": User.objects.all(),
        "selected_user": selected_user,
    })

def signup_view(request):
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # `role` handled inside form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = SimpleUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@user_passes_test(is_librarian)
def report_panel(request):
    today = now().date()
    month_start = today.replace(day=1)
    week_ago = today - timedelta(days=7)

    downloads_this_month = DownloadLog.objects.filter(timestamp__date__gte=month_start).count()

    top_viewed = DownloadLog.objects.values('pdf__title') \
        .annotate(total=Count('pdf')) \
        .order_by('-total')[:5]

    new_uploads = PDFBook.objects.filter(uploaded_at__date__gte=week_ago).count()

    return render(request, 'report_panel.html', {
        'downloads_this_month': downloads_this_month,
        'top_viewed': top_viewed,
        'new_uploads': new_uploads

    })



# views.py



def extract_public_id(url):
    """
    Extracts the public ID (without extension) from a Cloudinary URL.
    Example: https://res.cloudinary.com/.../upload/v1/pdfs/example -> 'pdfs/example'
    """
    match = re.search(r'/upload/(?:v\d+/)?(.+?)(?:\.pdf)?$', url)
    if match:
        return match.group(1)  # public ID without .pdf
    return None



def pdf_viewer(request, pk):
    pdf = get_object_or_404(PDFBook, pk=pk)

    public_id = extract_public_id(pdf.pdf_file)
    if not public_id:
        return render(request, 'pdf_error.html', {'message': 'Invalid PDF URL'})

    signed_url, _ = cloudinary_url(
        public_id,
        resource_type='raw',
        sign=True,
        format='pdf',     # 👈 forces .pdf extension in URL
        secure=True,
        expiry=300         # optional: link expires in 5 minutes
    )

    return render(request, 'pdf_viewer.html', {
        'pdf': pdf,
        'pdf_url': signed_url
    })

# Example: downloads/views.py
@login_required
def download_logs(request):
    logs = DownloadLog.objects.select_related('user', 'pdf').order_by('-timestamp')  # fixed
    return render(request, 'downloads/logs.html', {'logs': logs})


