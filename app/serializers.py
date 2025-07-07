from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Book, Author, Borrower, PDFBook, DownloadLog


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('Librarian', 'Librarian'), ('Reader', 'Reader')], write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        group = Group.objects.get(name=role)
        user.groups.add(group)
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
