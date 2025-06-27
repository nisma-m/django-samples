from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/add/', views.book_create, name='book_add'),
    path('book/edit/<int:pk>/', views.book_update, name='book_edit'),
    path('book/delete/<int:pk>/', views.book_delete, name='book_delete'),
    path('author/<int:pk>/', views.author_detail, name='author_detail'),
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('borrowings/', views.borrower_list, name='borrower_list'),
    path('borrow/return/<int:pk>/', views.mark_returned, name='mark_returned'),
]

