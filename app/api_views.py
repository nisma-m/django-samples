from rest_framework import generics, permissions, viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .permissions import IsSuperAdmin, IsSubAdmin
from .serializers import *
from .models import *

# ✅ Define User model once at the top
User = get_user_model()


# ✅ Register & Profile
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# ✅ Book - only Super Admin
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'genre', 'author__name']


# ✅ Borrower - Sub Admin only + log activity
class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [IsAuthenticated, IsSubAdmin]

    def perform_create(self, serializer):
        instance = serializer.save()
        if self.request.user.role == 'sub_admin':
            AuditLog.objects.create(
                user=self.request.user,
                action='Created Borrower',
                details=f'Borrower ID: {instance.id}'
            )

    def perform_update(self, serializer):
        instance = serializer.save()
        if self.request.user.role == 'sub_admin':
            AuditLog.objects.create(
                user=self.request.user,
                action='Updated Borrower',
                details=f'Borrower ID: {instance.id}'
            )


# ✅ PDFBook - both super and sub admins
class PDFBookViewSet(viewsets.ModelViewSet):
    queryset = PDFBook.objects.all()
    serializer_class = PDFBookSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsSubAdmin]


# ✅ Download Logs - Super Admin only
class DownloadLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DownloadLog.objects.all()
    serializer_class = DownloadLogSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


# ✅ Sub-admin Management - Super Admin only
class SubAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='sub_admin')
    serializer_class = SubAdminSerializer
    permission_classes = [IsSuperAdmin]

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='Updated Sub-admin',
            details=f'Updated sub-admin user ID {instance.id}'
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='Deleted Sub-admin',
            details=f'Deleted sub-admin user ID {instance.id}'
        )
        instance.delete()


# ✅ Audit Logs View - Super Admin only
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdmin]
