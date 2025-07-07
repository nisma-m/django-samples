# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Book, Author, Borrower, PDFBook, DownloadLog

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True)

    class Meta:
        model = Book
        fields = '__all__'

class BorrowerSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True)

    class Meta:
        model = Borrower
        fields = '__all__'

class PDFBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFBook
        fields = '__all__'

class DownloadLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    pdf = serializers.StringRelatedField()

    class Meta:
        model = DownloadLog
        fields = '__all__'

