from rest_framework import serializers
from .models import Book, IssuedBook, AdminActivityLog

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


from .models import Notification
from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class AdminActivityLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin_user.username', read_only=True)
    related_username = serializers.CharField(source='related_user.username', read_only=True)
    book_title = serializers.CharField(source='related_book.title', read_only=True)

    class Meta:
        model = AdminActivityLog
        fields = [
            'id', 'action', 'description', 'timestamp',
            'admin_user', 'admin_username',
            'related_user', 'related_username',
            'related_book', 'book_title'
        ]

