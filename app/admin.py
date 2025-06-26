
from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthdate')  # show in list view
    search_fields = ('name',)  # enable search bar

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'published_year')
    list_filter = ('genre', 'author')
    search_fields = ('title', 'genre')

