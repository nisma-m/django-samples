from django import forms
from .models import Book,Borrower,PDFBook
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

class PDFBookForm(forms.ModelForm):
    class Meta:
        model = PDFBook
        fields = ['title', 'author', 'pdf_file']




class SimpleUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '👤 Username',
                'autocomplete': 'off'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '🔒 Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '🔒 Confirm Password'
        })
