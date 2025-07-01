from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('signup/', views.signup_view, name='signup'),
    path('book/add/', views.book_create, name='book_add'),
    path('book/edit/<int:pk>/', views.book_update, name='book_edit'),
    path('book/delete/<int:pk>/', views.book_delete, name='book_delete'),
    path('author/<int:pk>/', views.author_detail, name='author_detail'),
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('borrowings/', views.borrower_list, name='borrower_list'),
    path('borrow/return/<int:pk>/', views.mark_returned, name='mark_returned'),
    path('upload/', views.upload_pdf, name='pdf_upload'),
    path('pdfs/', views.pdf_list, name='pdf_list'),
    path('pdfs/delete/<int:pk>/', views.pdf_delete, name='pdf_delete'),
    path('pdfs/download/<int:pk>/', views.download_pdf, name='download_pdf'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.report_panel, name='report_panel'),




]

