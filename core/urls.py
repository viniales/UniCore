from django.urls import path
from . import views

urlpatterns = [
    # Widok Niebieski (Lista)
    path('', views.widok_niebieski, name='widok_niebieski'),
    
    # Widok Zielony (Edycja)
    path('edycja/<int:przedmiot_id>/', views.edycja_sylabusa, name='edycja_sylabusa'),
    
    # Widok PDF (Wydruk) - TEGO BRAKOWAO
    path('drukuj/<int:przedmiot_id>/', views.sylabus_pdf, name='sylabus_pdf'),
]
