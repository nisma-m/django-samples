from django.db import models
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=100)
    birthdate = models.DateField()

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.title
    
class Borrower(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    borrow_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)

    def is_returned(self):
        return self.return_date is not None

    def __str__(self):
        return f"{self.name} - {self.book.title}"