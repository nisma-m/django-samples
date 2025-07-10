from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Book, IssuedBook
from .serializers import BookSerializer, IssueBookSerializer, IssuedBookHistorySerializer
from django.db.models import Q, F
from rest_framework import serializers
from django.db import transaction


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]



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

        # Decrement inside transaction
        book.available_copies -= 1
        book.save()

        issued = IssuedBook.objects.create(book=book, user=user)

        # Serialize again to get latest book.available_copies
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

        # ✅ Set return date
        issued.return_date = timezone.now()
        issued.save()

        # ✅ Increase available copies
        book = issued.book
        Book.objects.filter(id=book.id).update(available_copies=F('available_copies') + 1)

        # Optional: refresh to confirm
        book.refresh_from_db()
        print("Updated available copies:", book.available_copies)  # For debug only

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
