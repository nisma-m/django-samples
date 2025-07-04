
from django.contrib import admin
from .models import Author, Book , Borrower



# Inline Borrower inside Book Admin
class BorrowerInline(admin.TabularInline):
    model = Borrower
    extra = 0
    readonly_fields = ('name', 'email', 'borrow_date', 'return_date')
    can_delete = False
    show_change_link = True  # Optional: clickable to edit

# Author Admin
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthdate')  # Show in list view
    search_fields = ('name',)  # Enable search bar

# Book Admin with Borrower Inline, Filters, Search
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'published_year', 'available')
    list_filter = ('genre', 'author')
    search_fields = ('title', 'genre', 'author__name')
    inlines = [BorrowerInline]
    readonly_fields = ('available',)  # Optional: prevent editing manually

# Borrower Admin
@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'book', 'borrow_date', 'return_date', 'is_returned')
    list_filter = ('borrow_date', 'return_date')
    search_fields = ('name', 'book__title')
