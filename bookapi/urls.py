from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, IssueBookView, ReturnBookView, IssuedBookHistoryView, AdminIssuedBooksView
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register('books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('issue/', IssueBookView.as_view(), name='issue-book'),
    path('return/<int:pk>/', ReturnBookView.as_view(), name='return-book'),
    path('history/', IssuedBookHistoryView.as_view(), name='user-history'),
    path('admin-logs/', AdminIssuedBooksView.as_view(), name='admin-logs'),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

