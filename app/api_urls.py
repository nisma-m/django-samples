from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import SubAdminViewSet, AuditLogViewSet
from .api_views import (
    RegisterView, ProfileView,
    BookViewSet, BorrowerViewSet,
    PDFBookViewSet, DownloadLogViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('borrowers', BorrowerViewSet)
router.register('pdfs', PDFBookViewSet)
router.register('downloads', DownloadLogViewSet)
router.register('subadmins', SubAdminViewSet, basename='subadmin')
router.register('auditlogs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', ProfileView.as_view(), name='api_profile'),
    path('', include(router.urls)),  # ✅ only once
]

