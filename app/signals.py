from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Book, PDFBook, DownloadLog

@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    librarian_group, _ = Group.objects.get_or_create(name='Librarian')
    reader_group, _ = Group.objects.get_or_create(name='Reader')

    librarian_permissions = Permission.objects.filter(
        content_type__model__in=['book', 'pdfbook', 'downloadlog']
    )
    librarian_group.permissions.set(librarian_permissions)

    reader_permissions = Permission.objects.filter(codename__startswith='view_')
    reader_group.permissions.set(reader_permissions)
