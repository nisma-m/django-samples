from django.urls import path
from . import views
from django.contrib.auth.decorators import user_passes_test

def is_librarian(user):
    return user.groups.filter(name='Librarian').exists()

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('signup/', views.signup_view, name='signup'),
    
    # Librarian-only actions
    path('book/add/', user_passes_test(is_librarian)(views.book_create), name='book_add'),
    path('book/edit/<int:pk>/', user_passes_test(is_librarian)(views.book_update), name='book_edit'),
    path('book/delete/<int:pk>/', user_passes_test(is_librarian)(views.book_delete), name='book_delete'),
    path('upload/', user_passes_test(is_librarian)(views.upload_pdf), name='pdf_upload'),
    path('pdfs/delete/<int:pk>/', user_passes_test(is_librarian)(views.pdf_delete), name='pdf_delete'),
    path('dashboard/', user_passes_test(is_librarian)(views.dashboard), name='dashboard'),
    path('reports/', user_passes_test(is_librarian)(views.report_panel), name='report_panel'),

    # Reader and librarian shared
    path('author/<int:pk>/', views.author_detail, name='author_detail'),
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('borrowings/', views.borrower_list, name='borrower_list'),
    path('borrow/return/<int:pk>/', views.mark_returned, name='mark_returned'),
    path('pdfs/', views.pdf_list, name='pdf_list'),
    path('pdfs/download/<int:pk>/', views.download_pdf, name='download_pdf'),
    path('pdfs/view/<int:pk>/', views.pdf_viewer, name='pdf_viewer'),
    



]



