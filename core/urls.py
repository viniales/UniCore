from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_przedmiotow, name='lista_przedmiotow'),
    path('edycja/<int:przedmiot_id>/', views.edycja_sylabusa, name='edycja_sylabusa'),
    path('pdf/<int:przedmiot_id>/', views.pobierz_pdf, name='pobierz_pdf'),
]