from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    published_date = models.DateField()

    def __str__(self):
        return self.title


class IssuedBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.book.title}"
    

# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('book-issued', 'Book Issued'),
        ('book-returned', 'Book Returned'),
        ('overdue-alert', 'Overdue Alert'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(choices=NOTIFICATION_TYPES, max_length=20)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} - {self.user.username}"


class AdminActivityLog(models.Model):
    ACTION_TYPES = (
        ('add-book', 'Add Book'),
        ('update-book', 'Update Book'),
        ('delete-book', 'Delete Book'),
        ('issue-book', 'Issue Book'),
        ('return-book', 'Return Book'),
        ('change-permissions', 'Change Permissions'),
    )
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # ✅ Optional fields
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_actions')
    related_book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='book_logs')


    def __str__(self):
        return f"{self.admin_user.username} - {self.action} @ {self.timestamp}"
