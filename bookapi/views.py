from django.shortcuts import render
from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Book, IssuedBook, Notification,AdminActivityLog
from .serializers import (
    BookSerializer,
    IssueBookSerializer,
    IssuedBookHistorySerializer,
    AdminActivityLogSerializer,
    NotificationSerializer,
)
from django.db.models import Q, F
from django.db import transaction 
from rest_framework import generics, permissions


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        book = serializer.save()
        AdminActivityLog.objects.create(
        admin_user=self.request.user,  # ✅ instead of admin=
        action='book-added',
        description=f'Book "{book.title}" was added.'
    )


    def perform_update(self, serializer):
        book = serializer.save()
        AdminActivityLog.objects.create(
            admin_user=self.request.user,
            action='book-updated',
            description=f'Book "{book.title}" was updated.'
        )

    def perform_destroy(self, instance):
        AdminActivityLog.objects.create(
            admin_user=self.request.user,
            action='book-deleted',
            description=f'Book "{instance.title}" was deleted.'
        )
        instance.delete()


class IssueBookView(generics.CreateAPIView):
    serializer_class = IssueBookSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        book_id = request.data.get('book')
        user = request.user

        try:
            book = Book.objects.select_for_update().get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)

        if book.available_copies <= 0:
            return Response({"error": "No available copies"}, status=400)

        book.available_copies -= 1
        book.save()

        issued = IssuedBook.objects.create(book=book, user=user)

        # 📢 Notification for book issue
        Notification.objects.create(
            user=user,
            type='book-issued',
            message=f'Book "{book.title}" has been issued to you.',
        )
        AdminActivityLog.objects.create(
            admin_user=request.user,
            action='book-issued',
            description=f'Book "{book.title}" issued to {user.username}',
            related_user=user,
            related_book=book
        )


        issued.refresh_from_db()
        serializer = IssueBookSerializer(issued)
        return Response(serializer.data, status=201)


class ReturnBookView(generics.UpdateAPIView):
    serializer_class = IssueBookSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            issued = IssuedBook.objects.get(id=pk, user=request.user)
        except IssuedBook.DoesNotExist:
            return Response({"error": "Issued book not found"}, status=404)

        if issued.return_date:
            return Response({"error": "Book already returned"}, status=400)

        issued.return_date = timezone.now()
        issued.save()

        Book.objects.filter(id=issued.book.id).update(available_copies=F('available_copies') + 1)
        issued.book.refresh_from_db()

        # 📢 Notification for book return
        Notification.objects.create(
            user=request.user,
            type='book-returned',
            message=f'Book "{issued.book.title}" has been returned successfully.',
        )

        AdminActivityLog.objects.create(
            admin_user=request.user,
            action='book-returned',
            description=f'Book "{issued.book.title}" returned by {request.user.username}'
        )


        return Response({"message": "Book returned successfully"})


class IssuedBookHistoryView(generics.ListAPIView):
    serializer_class = IssuedBookHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = IssuedBook.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get('status')

        if status_param == 'returned':
            queryset = queryset.filter(return_date__isnull=False)
        elif status_param == 'issued':
            queryset = queryset.filter(return_date__isnull=True)

        return queryset


class AdminIssuedBooksView(generics.ListAPIView):
    serializer_class = IssuedBookHistorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = IssuedBook.objects.all()
        user_id = self.request.query_params.get('user')
        book_id = self.request.query_params.get('book')
        status_param = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')

        if user_id:
            queryset = queryset.filter(user__id=user_id)
        if book_id:
            queryset = queryset.filter(book__id=book_id)
        if status_param:
            if status_param.lower() == 'returned':
                queryset = queryset.filter(return_date__isnull=False)
            elif status_param.lower() == 'issued':
                queryset = queryset.filter(return_date__isnull=True)
        if start_date and end_date:
            queryset = queryset.filter(issue_date__range=[start_date, end_date])

        return queryset


# ✅ Notification Views

class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')


class MarkNotificationReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.user != request.user:
            return Response({'detail': 'Forbidden'}, status=403)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})


class AdminActivityLogListView(generics.ListAPIView):
    serializer_class = AdminActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = AdminActivityLog.objects.all().order_by('-timestamp')

        admin_id = self.request.query_params.get('admin')
        action = self.request.query_params.get('action')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if admin_id:
            queryset = queryset.filter(admin_user__id=admin_id)

        if action:
            queryset = queryset.filter(action=action)

        if start and end:
            queryset = queryset.filter(timestamp__range=[start, end])

        return queryset




