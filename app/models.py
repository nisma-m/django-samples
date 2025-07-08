from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from cloudinary_storage.storage import MediaCloudinaryStorage
from .storage import RawMediaCloudinaryStorage
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# ✅ Custom User Model

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('sub_admin', 'Sub Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
# ✅ Author
class Author(models.Model):
    name = models.CharField(max_length=100)
    birthdate = models.DateField()

    def __str__(self):
        return self.name

# ✅ Book
class Book(models.Model):
    GENRE_CHOICES = [
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Sci-Fi', 'Science Fiction'),
        ('Mystery', 'Mystery'),
        ('Romance', 'Romance'),
        ('Biography', 'Biography'),
    ]
    title = models.CharField(max_length=200)
    published_year = models.IntegerField()
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# ✅ Borrower
class Borrower(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)

    def is_returned(self):
        return self.return_date is not None

    def __str__(self):
        return f"{self.name} - {self.book.title}"

# ✅ PDFBook (Cloudinary with URLField)
class PDFBook(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    pdf_file = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ✅ DownloadLog
class DownloadLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pdf = models.ForeignKey(PDFBook, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.pdf.title} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
