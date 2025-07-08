from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Book, Author, Borrower, PDFBook, DownloadLog
from .models import AuditLog


User = get_user_model()

# User Profile Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')


# Registration Serializer with Role Validation
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def validate_role(self, value):
        allowed_roles = ['super_admin', 'sub_admin']
        if value not in allowed_roles:
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        return user


# Author Serializer
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


# Book Serializer with nested author and writable author_id
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True)

    class Meta:
        model = Book
        fields = '__all__'


# Borrower Serializer with nested book, writable book_id, and is_returned field
class BorrowerSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True)
    is_returned = serializers.SerializerMethodField()

    class Meta:
        model = Borrower
        fields = '__all__'

    def get_is_returned(self, obj):
        return obj.is_returned()


# PDFBook Serializer
class PDFBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFBook
        fields = '__all__'


# DownloadLog Serializer with string related fields for user and pdf
class DownloadLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    pdf = serializers.StringRelatedField()

    class Meta:
        model = DownloadLog
        fields = '__all__'

class SubAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active']
        read_only_fields = ['id', 'role']  # role is always sub_admin here

    def create(self, validated_data):
        validated_data['role'] = 'sub_admin'
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'details', 'timestamp']
