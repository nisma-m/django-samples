from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import Book, PDFBook, DownloadLog, Borrower
import logging

logger = logging.getLogger(__name__)

# 🔐 Create user roles after migrations
@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    librarian_group, _ = Group.objects.get_or_create(name='Librarian')
    reader_group, _ = Group.objects.get_or_create(name='Reader')

    # Librarian: full access to Book, PDFBook, DownloadLog
    librarian_permissions = Permission.objects.filter(
        content_type__model__in=['book', 'pdfbook', 'downloadlog']
    )
    librarian_group.permissions.set(librarian_permissions)

    # Reader: only view permissions
    reader_permissions = Permission.objects.filter(codename__startswith='view_')
    reader_group.permissions.set(reader_permissions)

# 📘 Log new Book added
@receiver(post_save, sender=Book)
def log_new_book(sender, instance, created, **kwargs):
    if created:
        logger.info(f'New Book Added: {instance.title} by {instance.author}')

# 🔁 Update Book availability on borrow/return
@receiver(post_save, sender=Borrower)
def update_book_availability(sender, instance, **kwargs):
    book = instance.book

    # If this borrower has returned the book
    if instance.return_date:
        # Check if *any* other borrower still has this book unreturned
        is_still_borrowed = Borrower.objects.filter(
            book=book,
            return_date__isnull=True
        ).exclude(id=instance.id).exists()

        book.available = not is_still_borrowed
    else:
        # Book is borrowed and not returned
        book.available = False

    book.save()
