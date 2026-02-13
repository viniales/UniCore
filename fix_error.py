import os

# 1. POPRAWNY VIEWS.PY (Upewniamy sie ze renderuje poprawnie)
views_content = """from django.shortcuts import render, get_object_or_404, redirect
from .models import Przedmiot, SzczegolySylabusa, TrescZajec
from .forms import SylabusForm

def edycja_sylabusa(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    sylabus, created = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)

    if request.method == 'POST':
        form = SylabusForm(request.POST, instance=sylabus)
        if form.is_valid():
            sylabus_obj = form.save()
            
            # Zapisz checkboxy
            wybrane_efekty = form.cleaned_data.get('efekty_kierunkowe')
            if wybrane_efekty is not None:
                przedmiot.efekty_kierunkowe.set(wybrane_efekty)
            
            # Zapisz harmonogram
            raw_text = form.cleaned_data.get('harmonogram_raw')
            if raw_text:
                TrescZajec.objects.filter(przedmiot=przedmiot).delete()
                lines = raw_text.strip().split('\\n')
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        TrescZajec.objects.create(przedmiot=przedmiot, numer_tematu=i, temat=line.strip(), liczba_godzin=2)
            
            return redirect('edycja_sylabusa', przedmiot_id=przedmiot.id)
    else:
        initial_data = {'efekty_kierunkowe': przedmiot.efekty_kierunkowe.all()}
        form = SylabusForm(instance=sylabus, initial=initial_data)

    tematy = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    return render(request, 'core/edycja_sylabusa.html', {'form': form, 'przedmiot': przedmiot, 'tematy': tematy})

def lista_przedmiotow(request):
    przedmioty = Przedmiot.objects.all()
    return render(request, 'core/lista.html', {'przedmioty': przedmioty})
"""

# 2. POPRAWNY URLS.PY (Bez nawiasow przy funkcjach)
urls_content = """from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_przedmiotow, name='lista_przedmiotow'),
    path('edycja/<int:przedmiot_id>/', views.edycja_sylabusa, name='edycja_sylabusa'),
]
"""

# ZAPISUJEMY PLIKI
base = os.getcwd()
with open(os.path.join(base, 'core', 'views.py'), 'w', encoding='utf-8') as f: f.write(views_content)
with open(os.path.join(base, 'core', 'urls.py'), 'w', encoding='utf-8') as f: f.write(urls_content)

print("✅ NAPRAWIONE: views.py i urls.py s teraz poprawne.")