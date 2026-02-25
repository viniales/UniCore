from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_przedmiotow, name='lista_przedmiotow'),
    path('kierunek/<int:kierunek_id>/', views.grid_kierunku, name='grid_kierunku'),
    path('edycja/<int:przedmiot_id>/', views.edycja_sylabusa, name='edycja_sylabusa'),
    path('pdf/<int:przedmiot_id>/', views.pobierz_pdf, name='pobierz_pdf'),
    path('zarzadzaj-przedmiotem/', views.zarzadzaj_przedmiotem, name='zarzadzaj_przedmiotem_nowy'),
    path('zarzadzaj-przedmiotem/<int:przedmiot_id>/', views.zarzadzaj_przedmiotem, name='zarzadzaj_przedmiotem'),
    path('dodaj-wykladowce/', views.dodaj_wykladowce, name='dodaj_wykladowce'),
    path('dodaj-kierunek/', views.dodaj_kierunek, name='dodaj_kierunek'),
]