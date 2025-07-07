
# views.py (API Views)
from rest_framework import generics, permissions, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *

# Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

# User Profile View
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# Book ViewSet
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'genre', 'author__name']

# Borrower ViewSet
class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

# PDF ViewSet
class PDFBookViewSet(viewsets.ModelViewSet):
    queryset = PDFBook.objects.all()
    serializer_class = PDFBookSerializer

# Download Log
class DownloadLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DownloadLog.objects.all()
    serializer_class = DownloadLogSerializer