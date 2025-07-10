from rest_framework import serializers
from .models import Book, IssuedBook

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class IssueBookSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)  # 👈 shows full book info in response
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), write_only=True, source='book'
    )  # 👈 accepts book_id in POST

    class Meta:
        model = IssuedBook
        fields = ['id', 'book', 'book_id', 'issue_date', 'return_date', 'fine', 'user']
        read_only_fields = ['user', 'issue_date', 'return_date', 'fine']

class IssuedBookHistorySerializer(serializers.ModelSerializer):
    book = BookSerializer()
    class Meta:
        model = IssuedBook
        fields = '__all__'
