from django import forms
from .models import Book,Borrower

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'published_year', 'genre', 'author']


# class BorrowerForm(forms.ModelForm):
#     class Meta:
#         model = Borrower
#         fields = ['name', 'email', 'book']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         borrowed_books = Borrower.objects.filter(return_date__isnull=True).values_list('book_id', flat=True)
#         available_books = Book.objects.exclude(id__in=borrowed_books)
#         self.fields['book'].queryset = available_books
#         self.fields['book'].empty_label = "Select an available book"

# from django import forms
# from .models import Borrower, Book

class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = ['name', 'email', 'book', 'borrow_date']  # ⛔ no return_date
        widgets = {
            'borrow_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        borrowed_books = Borrower.objects.filter(return_date__isnull=True).values_list('book_id', flat=True)
        self.fields['book'].queryset = Book.objects.exclude(id__in=borrowed_books)
        self.fields['book'].empty_label = "Select an available book"

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})