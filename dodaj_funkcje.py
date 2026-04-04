import os


def zapisz(sciezka, tresc):
    os.makedirs(os.path.dirname(sciezka) if os.path.dirname(sciezka) else ".", exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as f:
        f.write(tresc.strip())
    print(f"✅ Zaktualizowano: {sciezka}")


# ==========================================
# 1. MODELS.PY
# ==========================================
models = """
from django.db import models
from django.contrib.auth.models import User

class EfektUczenia(models.Model):
    KATEGORIE = [('W', 'Wiedza'), ('U', 'Umiejętności'), ('K', 'Kompetencje')]
    kod = models.CharField(max_length=20)
    kategoria = models.CharField(max_length=1, choices=KATEGORIE)
    opis = models.TextField()
    def __str__(self): return self.kod

class Wykladowca(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tytul = models.CharField(max_length=50, verbose_name="Tytuł", default="dr inż.")
    katedra = models.CharField(max_length=100, verbose_name="Katedra")
    def __str__(self): return f"{self.tytul} {self.user.first_name} {self.user.last_name}"

class EfektKierunkowy(models.Model):
    TYPY = [('W', 'Wiedza'), ('U', 'Umiejętności'), ('K', 'Kompetencje')]
    kod = models.CharField(max_length=20, verbose_name="Kod efektu")
    opis = models.TextField(verbose_name="Treść efektu")
    kategoria = models.CharField(max_length=1, choices=TYPY, default='W')
    def __str__(self): return f"{self.kod} - {self.opis[:50]}..."

class KierunekStudiow(models.Model):
    POZIOMY = [('1', 'Pierwszy stopień'), ('2', 'Drugi stopień')]
    FORMY = [('S', 'Stacjonarne'), ('N', 'Niestacjonarne')]
    nazwa = models.CharField(max_length=200)
    wydzial = models.CharField(max_length=200, default="Wydział Informatyki")
    poziom = models.CharField(max_length=1, choices=POZIOMY, default='1')
    forma = models.CharField(max_length=1, choices=FORMY, default='S')
    koordynator = models.ForeignKey(Wykladowca, on_delete=models.SET_NULL, null=True, blank=True, related_name='koordynowane_kierunki')
    def __str__(self): return self.nazwa

class Modul(models.Model):
    TYPY = [('Obowiązkowy', 'Obowiązkowy'), ('Wybieralny', 'Wybieralny')]
    kierunek = models.ForeignKey(KierunekStudiow, on_delete=models.CASCADE)
    kod_modulu = models.CharField(max_length=50)
    nazwa = models.CharField(max_length=200)
    typ = models.CharField(max_length=20, choices=TYPY)
    semestr = models.IntegerField()
    wymagane_ects = models.IntegerField()
    def __str__(self): return f"{self.kod_modulu} ({self.typ})"

class Przedmiot(models.Model):
    STATUSY = [
        ('ROBOCZY', 'W edycji (Wykładowca)'),
        ('WERYFIKACJA', 'Do sprawdzenia (Szef Kierunku)'),
        ('DO_POPRAWY', 'Do poprawy (Odrzucony)'),
        ('SPRAWDZONY', 'Sprawdzony (Koordynator Kierunku)'),
        ('ZATWIERDZONY', 'Zatwierdzony (Prodziekan)')
    ]
    modul = models.ForeignKey(Modul, on_delete=models.CASCADE, related_name='przedmioty')
    status = models.CharField(max_length=20, choices=STATUSY, default='ROBOCZY')
    uwagi_statusu = models.TextField(blank=True, default="", verbose_name="Uwagi do sylabusa")
    nazwa_pl = models.CharField(max_length=255)
    nazwa_en = models.CharField(max_length=255, blank=True)
    kod_przedmiotu = models.CharField(max_length=50)
    jezyk_wykladowy = models.CharField(max_length=50, default="Polski")
    cykl_dydaktyczny = models.CharField(max_length=20, default="2026/2027")
    badania_naukowe = models.BooleanField(default=False)
    ects = models.IntegerField()
    godz_wyklad = models.IntegerField(default=0)
    godz_cwiczenia = models.IntegerField(default=0)
    godz_lab = models.IntegerField(default=0)
    godz_projekt = models.IntegerField(default=0)
    godz_seminarium = models.IntegerField(default=0)
    godz_egzamin = models.IntegerField(default=0)
    efekty_kierunkowe = models.ManyToManyField(EfektKierunkowy, blank=True)
    koordynatorzy = models.ManyToManyField(Wykladowca, related_name='przypisane_przedmioty', blank=True)
    def __str__(self): return self.nazwa_pl

# --- NOWY MODEL CZATU ---
class Komentarz(models.Model):
    przedmiot = models.ForeignKey(Przedmiot, on_delete=models.CASCADE, related_name='komentarze')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    tresc = models.TextField()
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Komentarz {self.autor.username} - {self.data_utworzenia}"

class SzczegolySylabusa(models.Model):
    przedmiot = models.OneToOneField(Przedmiot, on_delete=models.CASCADE, related_name='sylabus')
    opis_wstepny = models.TextField(blank=True, default="")
    wymagania_wstepne = models.TextField(blank=True, default="")
    efekty_wiedza = models.TextField(default="-", blank=True)
    efekty_umiejetnosci = models.TextField(default="-", blank=True)
    efekty_kompetencje = models.TextField(default="-", blank=True)
    mapowanie_efektow = models.TextField(blank=True, default="")
    metody_nauczania = models.TextField(blank=True, default="")
    formy_oceny = models.TextField(blank=True, default="")
    zasady_oceniania = models.TextField(default="Zgodnie z regulaminem...", blank=True)
    odrabianie_zajec = models.TextField(default="Konsultacja z prowadzącym...", blank=True)
    wymagania_obecnosci = models.TextField(default="Obecność obowiązkowa...", blank=True)
    pw_przygotowanie_cw = models.IntegerField(default=0, blank=True, null=True)
    pw_sprawozdania = models.IntegerField(default=0, blank=True, null=True)
    pw_projekt = models.IntegerField(default=0, blank=True, null=True)
    pw_wyklad = models.IntegerField(default=0, blank=True, null=True)
    pw_egzamin = models.IntegerField(default=0, blank=True, null=True)
    pw_literatura = models.IntegerField(default=0, blank=True, null=True)
    literatura = models.TextField(blank=True, default="")
    inne_informacje = models.TextField(blank=True, default="")

class TrescZajec(models.Model):
    przedmiot = models.ForeignKey(Przedmiot, on_delete=models.CASCADE, related_name='harmonogram')
    numer_tematu = models.IntegerField()
    temat = models.TextField()
    liczba_godzin = models.IntegerField()
"""

# ==========================================
# 2. FORMS.PY
# ==========================================
forms_py = """
from django import forms
from django.contrib.auth.models import User
from .models import SzczegolySylabusa, Przedmiot, EfektKierunkowy, Wykladowca, Modul, KierunekStudiow

class SylabusForm(forms.ModelForm):
    efekty_kierunkowe = forms.ModelMultipleChoiceField(queryset=EfektKierunkowy.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    harmonogram_raw = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control border-primary shadow-sm', 'rows': 5}), required=False)
    class Meta:
        model = SzczegolySylabusa
        exclude = ['przedmiot', 'inne_informacje']
        widgets = {
            'wymagania_wstepne': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'metody_nauczania': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'formy_oceny': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'zasady_oceniania': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'odrabianie_zajec': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'wymagania_obecnosci': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'literatura': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields: self.fields[field].required = False

class PrzedmiotForm(forms.ModelForm):
    kierunek = forms.ModelChoiceField(queryset=KierunekStudiow.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    typ_zajec = forms.ChoiceField(choices=Modul.TYPY, widget=forms.Select(attrs={'class': 'form-select'}))
    semestr = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Przedmiot
        fields = ['status', 'nazwa_pl', 'nazwa_en', 'kod_przedmiotu', 'ects', 'jezyk_wykladowy', 'cykl_dydaktyczny',
                  'badania_naukowe', 'godz_wyklad', 'godz_cwiczenia', 'godz_lab', 'godz_projekt', 'godz_seminarium',
                  'godz_egzamin', 'koordynatorzy']
        widgets = {
            'koordynatorzy': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-select border-primary shadow-sm fw-bold'}),
        }

class KierunekForm(forms.ModelForm):
    class Meta:
        model = KierunekStudiow
        fields = '__all__'

class WykladowcaUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    tytul = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    katedra = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
"""

# ==========================================
# 3. VIEWS.PY
# ==========================================
views_py = """
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from .models import Przedmiot, SzczegolySylabusa, TrescZajec, KierunekStudiow, Modul, EfektKierunkowy, Wykladowca, Komentarz
from .forms import SylabusForm, PrzedmiotForm, WykladowcaUserForm, KierunekForm
from django.db.models import Sum
import re

@login_required
def lista_przedmiotow(request):
    wykladowca = getattr(request.user, 'wykladowca', None)
    is_admin = request.user.is_superuser

    if is_admin:
        kierunki_pod_opieka = KierunekStudiow.objects.all()
        przedmioty_kierunku = Przedmiot.objects.all()
        moje_prowadzone = Przedmiot.objects.filter(koordynatorzy__user=request.user)
        tryb_nazwa = "Panel Prodziekana"
    elif wykladowca:
        kierunki_pod_opieka = KierunekStudiow.objects.filter(koordynator=wykladowca)
        przedmioty_kierunku = Przedmiot.objects.filter(modul__kierunek__in=kierunki_pod_opieka)
        moje_prowadzone = Przedmiot.objects.filter(koordynatorzy=wykladowca)
        tryb_nazwa = "Panel Wykładowcy / Koordynatora"
    else:
        return HttpResponse("Błąd: Brak uprawnień profilowych.")

    wszystkie_widoczne = (przedmioty_kierunku | moje_prowadzone).distinct()

    statystyki_ects = []
    for k in kierunki_pod_opieka:
        semestry_data = []
        for s in range(1, 9):
            przedmioty_sem = Przedmiot.objects.filter(modul__kierunek=k, modul__semestr=s)
            suma = przedmioty_sem.aggregate(Sum('ects'))['ects__sum'] or 0
            liczba = przedmioty_sem.count()
            if liczba > 0:
                semestry_data.append({'numer': s, 'suma': suma, 'liczba': liczba, 'alert': suma != 30})
        if semestry_data:
            statystyki_ects.append({'id': k.id, 'nazwa': k.nazwa, 'semestry': semestry_data})

    return render(request, 'core/panel_zarzadzania.html', {
        'przedmioty': wszystkie_widoczne,
        'przedmioty_kierunku_ids': list(przedmioty_kierunku.values_list('id', flat=True)),
        'moje_przedmioty_ids': list(moje_prowadzone.values_list('id', flat=True)),
        'statystyki_ects': statystyki_ects,
        'tryb': tryb_nazwa,
        'is_dean': is_admin
    })

@login_required
def zarzadzaj_przedmiotem(request, przedmiot_id=None):
    is_dean = request.user.is_superuser
    wykladowca = getattr(request.user, 'wykladowca', None)

    if przedmiot_id:
        przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
        if not is_dean and przedmiot.modul.kierunek.koordynator != wykladowca:
            return HttpResponseForbidden("Brak uprawnień.")
    else:
        if not is_dean: return HttpResponseForbidden("Tylko Prodziekan dodaje przedmioty.")
        przedmiot = None

    if request.method == 'POST':
        if 'dodaj_komentarz' in request.POST and przedmiot:
            tresc = request.POST.get('tresc_komentarza')
            if tresc: Komentarz.objects.create(przedmiot=przedmiot, autor=request.user, tresc=tresc)
            return redirect('zarzadzaj_przedmiotem', przedmiot_id=przedmiot.id)

        form = PrzedmiotForm(request.POST, instance=przedmiot)
        if form.is_valid():
            p = form.save(commit=False)
            if not is_dean and p.status == 'ZATWIERDZONY': p.status = 'SPRAWDZONY'

            k = form.cleaned_data['kierunek']
            s = form.cleaned_data['semestr']
            t = form.cleaned_data['typ_zajec']

            modul, _ = Modul.objects.get_or_create(
                kierunek=k, semestr=s, typ=t,
                defaults={'kod_modulu': f"{k.nazwa[:3].upper()}-{s}-{t[:3].upper()}", 'nazwa': f"{t} - Semestr {s}", 'wymagane_ects': 30}
            )
            p.modul = modul
            p.save()
            form.save_m2m()

            usun_ids = request.POST.getlist('usun_efekt')
            if usun_ids: p.efekty_kierunkowe.remove(*usun_ids)

            for kt, op in zip(request.POST.getlist('nowy_efekt_kat'), request.POST.getlist('nowy_efekt_opis')):
                if op.strip():
                    max_num = max([0] + [int(re.search(r'(\d+)$', e.kod).group(1)) for e in EfektKierunkowy.objects.filter(kategoria=kt) if re.search(r'(\d+)$', e.kod)])
                    p.efekty_kierunkowe.add(EfektKierunkowy.objects.create(kod=f"K_{kt}{max_num + 1:02d}", kategoria=kt, opis=op.strip()))

            p.save()
            return redirect('lista_przedmiotow')
    else:
        initial_data = {'kierunek': przedmiot.modul.kierunek, 'semestr': przedmiot.modul.semestr, 'typ_zajec': przedmiot.modul.typ} if przedmiot and hasattr(przedmiot, 'modul') else {}
        form = PrzedmiotForm(instance=przedmiot, initial=initial_data)

    return render(request, 'core/formularz_przedmiotu.html', {'form': form, 'przedmiot': przedmiot, 'is_dean': is_dean})

@login_required
def edycja_sylabusa(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    wykladowca = getattr(request.user, 'wykladowca', None)

    if not request.user.is_superuser and wykladowca not in przedmiot.koordynatorzy.all():
        return HttpResponseForbidden("Brak uprawnień.")

    sylabus, _ = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)

    if request.method == 'POST':
        if 'dodaj_komentarz' in request.POST:
            tresc = request.POST.get('tresc_komentarza')
            if tresc: Komentarz.objects.create(przedmiot=przedmiot, autor=request.user, tresc=tresc)
            return redirect('edycja_sylabusa', przedmiot_id=przedmiot.id)

        form = SylabusForm(request.POST, instance=sylabus)
        if form.is_valid():
            form.save()
            wybrane = form.cleaned_data.get('efekty_kierunkowe')
            if wybrane is not None: przedmiot.efekty_kierunkowe.set(wybrane)

            raw = form.cleaned_data.get('harmonogram_raw')
            if raw:
                TrescZajec.objects.filter(przedmiot=przedmiot).delete()
                for i, line in enumerate(raw.strip().split('\\n'), 1):
                    if line.strip(): TrescZajec.objects.create(przedmiot=przedmiot, numer_tematu=i, temat=line.strip(), liczba_godzin=2)

                        if 'przekaz_dalej' in request.POST:
                            przedmiot.status = 'WERYFIKACJA'
                            przedmiot.save()
                            return redirect('lista_przedmiotow')

            return redirect('edycja_sylabusa', przedmiot_id=przedmiot.id)
    else:
        form = SylabusForm(instance=sylabus, initial={
            "efekty_kierunkowe": przedmiot.efekty_kierunkowe.all(),
            "harmonogram_raw": "\\n".join([t.temat for t in TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')])
        })
        form.fields["efekty_kierunkowe"].queryset = przedmiot.efekty_kierunkowe.all()

    tematy_zdekodowane, counters = [], {}
    for t in TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu'):
        tresc, forma, efekty = t.temat, 'wykład', ''
        if tresc.startswith('['):
            end_idx = tresc.find(']')
            if end_idx != -1:
                meta, tresc = tresc[1:end_idx], tresc[end_idx + 1:].strip()
                parts = meta.split('|')
                forma = parts[0].strip()
                if len(parts) > 1: efekty = parts[1].strip()
        counters[forma] = counters.get(forma, 0) + 1
        tematy_zdekodowane.append({'lp': counters[forma], 'tresc': tresc, 'efekty': efekty, 'forma': forma})

    return render(request, 'core/edycja_sylabusa.html', {'form': form, 'przedmiot': przedmiot, 'tematy': tematy_zdekodowane})

# --- NOWE FUNKCJE KLONOWANIA ---
def wykonaj_klonowanie(stary_p):
    try:
        lata = stary_p.cykl_dydaktyczny.split('/')
        nowy_cykl = f"{int(lata[0])+1}/{int(lata[1])+1}"
    except:
        nowy_cykl = stary_p.cykl_dydaktyczny + " (Kopia)"

    stare_efekty = list(stary_p.efekty_kierunkowe.all())
    stali_koordynatorzy = list(stary_p.koordynatorzy.all())
    stary_harmonogram = list(stary_p.harmonogram.all())
    try: stary_sylabus = stary_p.sylabus
    except SzczegolySylabusa.DoesNotExist: stary_sylabus = None

    stary_p.pk = None
    stary_p.status = 'ROBOCZY'
    stary_p.cykl_dydaktyczny = nowy_cykl
    stary_p.save()

    stary_p.efekty_kierunkowe.set(stare_efekty)
    stary_p.koordynatorzy.set(stali_koordynatorzy)

    if stary_sylabus:
        stary_sylabus.pk = None
        stary_sylabus.przedmiot = stary_p
        stary_sylabus.save()
    else:
        SzczegolySylabusa.objects.create(przedmiot=stary_p)

    for t in stary_harmonogram:
        t.pk = None
        t.przedmiot = stary_p
        t.save()

@login_required
def klonuj_kierunek(request, kierunek_id):
    if not request.user.is_superuser: return HttpResponseForbidden()
    przedmioty = Przedmiot.objects.filter(modul__kierunek_id=kierunek_id)
    for p in przedmioty: wykonaj_klonowanie(p)
    return redirect('lista_przedmiotow')

@login_required
def klonuj_przedmiot_widok(request, przedmiot_id):
    if not request.user.is_superuser: return HttpResponseForbidden()
    wykonaj_klonowanie(get_object_or_404(Przedmiot, id=przedmiot_id))
    return redirect('lista_przedmiotow')

# Reszta funkcji bez zmian
@login_required
def grid_kierunku(request, kierunek_id): return HttpResponse("W budowie")

@login_required
def pobierz_pdf(request, przedmiot_id): pass

@login_required
def dodaj_wykladowce(request): pass

@login_required
def dodaj_kierunek(request): pass
"""

# ==========================================
# 4. URLS.PY
# ==========================================
urls_py = """
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.lista_przedmiotow, name='lista_przedmiotow'),
    path('kierunek/<int:kierunek_id>/', views.grid_kierunku, name='grid_kierunku'),
    path('edycja/<int:przedmiot_id>/', views.edycja_sylabusa, name='edycja_sylabusa'),
    path('pdf/<int:przedmiot_id>/', views.pobierz_pdf, name='pobierz_pdf'),
    path('zarzadzaj-przedmiotem/', views.zarzadzaj_przedmiotem, name='zarzadzaj_przedmiotem_nowy'),
    path('zarzadzaj-przedmiotem/<int:przedmiot_id>/', views.zarzadzaj_przedmiotem, name='zarzadzaj_przedmiotem'),
    path('dodaj-wykladowce/', views.dodaj_wykladowce, name='dodaj_wykladowce'),
    path('dodaj-kierunek/', views.dodaj_kierunek, name='dodaj_kierunek'),

    # --- NOWE SCIEZKI DO KLONOWANIA ---
    path('klonuj-kierunek/<int:kierunek_id>/', views.klonuj_kierunek, name='klonuj_kierunek'),
    path('klonuj-przedmiot/<int:przedmiot_id>/', views.klonuj_przedmiot_widok, name='klonuj_przedmiot'),
]
"""

# ==========================================
# 5. PANEL_ZARZADZANIA.HTML
# ==========================================
panel_html = """
{% extends 'core/base.html' %}
{% block content %}
<style>
    :root { --primary-blue: #2563eb; --primary-green: #10b981; --bg-color: #f8fafc; --card-border: #e2e8f0; }
    body { background-color: var(--bg-color); }
    .semester-card { background: white; border-radius: 12px; border: 1px solid var(--card-border); transition: transform 0.2s ease, box-shadow 0.2s ease; padding: 1.25rem; }
    .semester-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    .ects-progress { height: 6px; border-radius: 3px; background-color: #e2e8f0; overflow: hidden; margin: 10px 0; }
    .ects-bar { height: 100%; transition: width 0.3s ease; }
    .table-modern { border-collapse: separate; border-spacing: 0 0.5rem; }
    .table-modern th { border: none; color: #64748b; font-weight: 600; font-size: 0.8rem; letter-spacing: 0.5px; padding-bottom: 0.5rem; }
    .table-modern tr { background-color: white; box-shadow: 0 1px 2px rgba(0,0,0,0.03); transition: box-shadow 0.2s; }
    .table-modern tr:hover { box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); }
    .table-modern td { padding: 1rem 1.25rem; border: none; border-top: 1px solid var(--card-border); border-bottom: 1px solid var(--card-border); vertical-align: middle; }
    .table-modern td:first-child { border-left: 1px solid var(--card-border); border-top-left-radius: 10px; border-bottom-left-radius: 10px; }
    .table-modern td:last-child { border-right: 1px solid var(--card-border); border-top-right-radius: 10px; border-bottom-right-radius: 10px; }
    .status-pill { padding: 0.35rem 0.8rem; border-radius: 50px; font-weight: 600; font-size: 0.75rem; white-space: nowrap; }
    .section-title { font-size: 1.25rem; font-weight: 700; color: #1e293b; display: flex; align-items: center; }
    .section-icon-box { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px; color: white; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>

<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-5 pb-3 border-bottom">
        <div>
            <h1 class="fw-bold text-dark mb-1 fs-3"><i class="fa-solid fa-layer-group text-primary me-2"></i>{{ tryb }}</h1>
            <p class="text-muted small mb-0">System zarządzania programami studiów</p>
        </div>
        {% if is_dean %}
        <div class="d-flex gap-2">
            <a href="{% url 'dodaj_wykladowce' %}" class="btn btn-outline-secondary rounded-3 px-3 shadow-sm bg-white"><i class="fa-solid fa-user-plus me-2"></i>Wykładowca</a>
            <a href="{% url 'dodaj_kierunek' %}" class="btn btn-outline-secondary rounded-3 px-3 shadow-sm bg-white"><i class="fa-solid fa-graduation-cap me-2"></i>Kierunek</a>
            <a href="{% url 'zarzadzaj_przedmiotem_nowy' %}" class="btn btn-primary rounded-3 px-4 shadow-sm fw-bold"><i class="fa-solid fa-plus me-2"></i>Nowy Przedmiot</a>
        </div>
        {% endif %}
    </div>

    {% if statystyki_ects %}
    <div class="mb-5">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
            <div class="d-flex align-items-center">
                <div class="section-icon-box bg-primary shadow-sm"><i class="fa-solid fa-sliders"></i></div>
                <h3 class="section-title mb-0">Nadzór nad Kierunkami</h3>
            </div>
            <div class="d-flex align-items-center bg-white p-2 rounded-3 shadow-sm border">
                <label for="kierunekFilter" class="fw-bold text-secondary mb-0 me-3 ms-2 small text-uppercase">
                    <i class="fa-solid fa-filter me-1 text-primary"></i> Wybierz:
                </label>
                <select id="kierunekFilter" class="form-select form-select-sm border-0 fw-bold text-dark" style="min-width: 280px; background-color: #f1f5f9;" onchange="filterKierunki()">
                    <option value="all">Pokaż wszystkie kierunki</option>
                    {% for s_k in statystyki_ects %}
                    <option value="{{ s_k.nazwa|slugify }}">{{ s_k.nazwa }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        {% for s_k in statystyki_ects %}
        <div class="kierunek-block mb-5 bg-white p-4 rounded-4 shadow-sm border border-light" data-kierunek-id="{{ s_k.nazwa|slugify }}">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="fw-bold text-dark mb-0"><i class="fa-solid fa-folder-tree text-muted me-2"></i>{{ s_k.nazwa }}</h5>
                {% if is_dean %}
                <a href="/klonuj-kierunek/{{ s_k.id }}/" class="btn btn-sm btn-outline-primary shadow-sm fw-bold" onclick="return confirm('Skopiować absolutnie wszystkie przedmioty tego kierunku na nowy rok akademicki?')">
                    <i class="fa-solid fa-clone me-1"></i> Skopiuj na kolejny rok
                </a>
                {% endif %}
            </div>

            <div class="row g-3 mb-4">
                {% for sem in s_k.semestry %}
                <div class="col-md-3 col-sm-6">
                    <div class="semester-card">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="small text-uppercase fw-bold text-muted">Semestr {{ sem.numer }}</span>
                            <i class="fa-solid {% if sem.alert %}fa-circle-exclamation text-danger{% else %}fa-circle-check text-success{% endif %}"></i>
                        </div>
                        <div class="d-flex align-items-baseline gap-1">
                            <span class="fs-4 fw-bold {% if sem.alert %}text-danger{% else %}text-dark{% endif %}">{{ sem.suma }}</span>
                            <span class="small text-muted">/ 30 ECTS</span>
                        </div>
                        <div class="ects-progress">
                            <div class="ects-bar {% if sem.alert %}bg-danger{% else %}bg-primary{% endif %}" style="width: {% widthratio sem.suma 30 100 %}%; max-width: 100%;"></div>
                        </div>
                        <div class="small fw-semibold text-secondary mt-2"><i class="fa-solid fa-book me-1 opacity-50"></i> Przedmiotów: {{ sem.liczba }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="table-responsive">
                <table class="table table-modern align-middle mb-0">
                    <thead>
                        <tr><th class="ps-4">PRZEDMIOT</th><th>KIERUNEK / SEMESTR</th><th>ECTS</th><th>STATUS</th><th class="text-end pe-4">ZARZĄDZANIE</th></tr>
                    </thead>
                    <tbody>
                        {% for p in przedmioty %}{% if p.id in przedmioty_kierunku_ids and p.modul.kierunek.nazwa == s_k.nazwa %}
                        <tr>
                            <td class="ps-4" style="width: 35%;">
                                <div class="fw-bold text-dark fs-6">{{ p.nazwa_pl }}</div>
                                <div class="text-muted small" style="font-family: monospace;">{{ p.kod_przedmiotu }}</div>
                            </td>
                            <td>
                                <div class="small fw-bold text-secondary">{{ p.modul.kierunek.nazwa }}</div>
                                <span class="badge bg-light text-dark border mt-1">Semestr {{ p.modul.semestr }} ({{ p.cykl_dydaktyczny }})</span>
                            </td>
                            <td><span class="badge bg-primary-subtle text-primary px-2 py-1 fs-6 rounded-3">{{ p.ects }}</span></td>
                            <td>
                                {% if p.status == 'ZATWIERDZONY' %}<span class="status-pill bg-success-subtle text-success border border-success-subtle"><i class="fa-solid fa-check-double me-1"></i>Zatwierdzony ostatecznie</span>
                                {% elif p.status == 'SPRAWDZONY' %}{% if is_dean %}<span class="status-pill bg-info-subtle text-info-emphasis border border-info-subtle"><i class="fa-solid fa-clock me-1"></i>Czeka na Ciebie (Prodziekan)</span>{% else %}<span class="status-pill bg-primary-subtle text-primary border border-primary-subtle"><i class="fa-solid fa-paper-plane me-1"></i>Przekazano Prodziekanowi</span>{% endif %}
                                {% elif p.status == 'WERYFIKACJA' %}{% if is_dean %}<span class="status-pill bg-light text-secondary border"><i class="fa-solid fa-hourglass-start me-1"></i>Czeka na Szefa Kierunku</span>{% else %}<span class="status-pill bg-info-subtle text-info-emphasis border border-info-subtle"><i class="fa-solid fa-clock me-1"></i>Czeka na Ciebie</span>{% endif %}
                                {% elif p.status == 'DO_POPRAWY' %}<span class="status-pill bg-danger-subtle text-danger border border-danger-subtle"><i class="fa-solid fa-triangle-exclamation me-1"></i>Odrzucony do poprawy</span>
                                {% else %}<span class="status-pill bg-light text-secondary border"><i class="fa-solid fa-pen-nib me-1"></i>W edycji u prowadzącego</span>{% endif %}
                            </td>
                            <td class="text-end pe-4 text-nowrap">
                                <a href="{% url 'zarzadzaj_przedmiotem' p.id %}" class="btn btn-sm btn-light border px-3 py-2 rounded-3 text-primary fw-bold shadow-sm hover-primary"><i class="fa-solid fa-gear me-2"></i>Struktura</a>
                                {% if is_dean %}
                                <a href="/klonuj-przedmiot/{{ p.id }}/" class="btn btn-sm btn-outline-primary ms-1 rounded-3 px-3 py-2 shadow-sm" title="Klonuj przedmiot na nowy rok" onclick="return confirm('Stworzyć dokładną kopię na kolejny rok akademicki?')"><i class="fa-solid fa-clone"></i></a>
                                {% endif %}
                                <a href="{% url 'pobierz_pdf' p.id %}" class="btn btn-sm btn-outline-danger ms-1 rounded-3 px-3 py-2 shadow-sm" target="_blank" title="Pobierz i sprawdź PDF"><i class="fa-solid fa-file-pdf"></i></a>
                            </td>
                        </tr>
                        {% endif %}{% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endfor %}
        <div id="noResultsMsg" class="text-center py-5 text-muted" style="display: none;"><i class="fa-solid fa-magnifying-glass fs-1 mb-3 opacity-25"></i><h5>Brak kierunków do wyświetlenia.</h5></div>
    </div>
    {% endif %}

    {% if moje_przedmioty_ids %}
    <div class="mt-5">
        <div class="d-flex align-items-center mb-4">
            <div class="section-icon-box shadow-sm" style="background-color: var(--primary-green);"><i class="fa-solid fa-pen-nib"></i></div>
            <h3 class="section-title mb-0">Twoje Sylabusy</h3>
        </div>
        <div class="table-responsive bg-white p-4 rounded-4 shadow-sm border border-light">
            <table class="table table-modern align-middle mb-0">
                <thead><tr><th class="ps-4">NAZWA PRZEDMIOTU</th><th>KIERUNEK</th><th>STATUS</th><th class="text-end pe-4">EDYCJA SYLABUSA</th></tr></thead>
                <tbody>
                    {% for p in przedmioty %}{% if p.id in moje_przedmioty_ids %}
                    <tr>
                        <td class="ps-4" style="width: 40%;">
                            <div class="fw-bold text-dark fs-6">{{ p.nazwa_pl }}</div>
                            <div class="text-muted small d-flex gap-2 align-items-center">
                                <span style="font-family: monospace;">{{ p.kod_przedmiotu }}</span><span class="text-light-subtle">|</span><span>ECTS: {{ p.ects }}</span>
                            </div>
                        </td>
                        <td>
                            <div class="small fw-bold text-secondary">{{ p.modul.kierunek.nazwa }}</div>
                            <span class="badge bg-light text-dark border mt-1">Semestr {{ p.modul.semestr }} ({{ p.cykl_dydaktyczny }})</span>
                        </td>
                        <td>
                            {% if p.status == 'ZATWIERDZONY' %}<span class="status-pill bg-success-subtle text-success border border-success-subtle"><i class="fa-solid fa-check-double me-1"></i>Zatwierdzony Ostatecznie!</span>
                            {% elif p.status == 'SPRAWDZONY' %}<span class="status-pill bg-primary-subtle text-primary border border-primary-subtle"><i class="fa-solid fa-thumbs-up me-1"></i>Zaakceptowany przez Szefa</span>
                            {% elif p.status == 'WERYFIKACJA' %}<span class="status-pill bg-info-subtle text-info-emphasis border border-info-subtle"><i class="fa-solid fa-paper-plane me-1"></i>Wysłano do akceptacji</span>
                            {% elif p.status == 'DO_POPRAWY' %}<span class="status-pill bg-danger-subtle text-danger border border-danger-subtle"><i class="fa-solid fa-circle-exclamation me-1"></i>Wymaga poprawy!</span>
                            {% else %}<span class="status-pill bg-warning-subtle text-warning-emphasis border border-warning-subtle"><i class="fa-solid fa-pen-nib me-1"></i>Szkic roboczy</span>{% endif %}
                        </td>
                        <td class="text-end pe-4 text-nowrap">
                            <a href="{% url 'edycja_sylabusa' p.id %}" class="btn btn-sm btn-success px-3 py-2 rounded-3 shadow-sm fw-bold"><i class="fa-solid fa-pen-to-square me-2"></i>Edytuj</a>
                            <a href="{% url 'pobierz_pdf' p.id %}" class="btn btn-sm btn-outline-danger ms-2 rounded-3 px-3 py-2 shadow-sm" target="_blank" title="Pobierz PDF"><i class="fa-solid fa-file-pdf"></i></a>
                        </td>
                    </tr>
                    {% endif %}{% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
</div>

<script>
function filterKierunki() {
    const selectedId = document.getElementById('kierunekFilter').value;
    const blocks = document.querySelectorAll('.kierunek-block');
    let visibleCount = 0;
    blocks.forEach(block => {
        if (selectedId === 'all' || block.getAttribute('data-kierunek-id') === selectedId) {
            block.style.display = 'block'; block.style.animation = 'fadeIn 0.3s ease-in-out'; visibleCount++;
        } else { block.style.display = 'none'; }
    });
    document.getElementById('noResultsMsg').style.display = visibleCount === 0 ? 'block' : 'none';
}
</script>
{% endblock %}
"""

# ==========================================
# 6. CZAT W FORMULARZ_PRZEDMIOTU.HTML (PODMIANA CZESCIOWA)
# ==========================================
form_html = """
{% extends 'core/base.html' %}
{% block content %}
<style>
    .field-locked { background-color: #f8f9fa !important; border: 1px solid #dee2e6 !important; opacity: 0.8; pointer-events: none; }
    .field-editable { background-color: #ffffff !important; border: 1px solid #0d6efd !important; border-left-width: 4px !important; }
    .section-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; display: block; }
</style>

<div class="container py-4">
    {% if form.errors %}
    <div class="alert alert-danger shadow-sm border-start border-danger border-4 mb-4">
        <h5 class="fw-bold"><i class="fa-solid fa-circle-exclamation me-2"></i>Błąd walidacji:</h5>
        <ul class="mb-0">{% for field, errors in form.errors.items %}<li><strong>{{ field }}:</strong> {{ errors|striptags }}</li>{% endfor %}</ul>
    </div>
    {% endif %}

    <div class="card shadow border-0 p-4 p-md-5 mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
            <div>
                <h2 class="text-primary fw-bold mb-0">{% if is_dean %}Zarządzanie Przedmiotem{% else %}Nadzór nad Przedmiotem{% endif %}</h2>
                <p class="small text-muted mt-1 mb-0">Pola <span class="badge bg-secondary">Szare</span> są zablokowane dla Koordynatora.</p>
            </div>
            <div class="badge bg-dark p-2 fs-6 shadow-sm"><i class="fa-solid fa-user-tie me-2"></i>{% if is_dean %}Prodziekan{% else %}Koordynator Kierunku{% endif %}</div>
        </div>

        <div class="mb-5 p-4 rounded-4 shadow-sm" style="background-color: #f8fafc; border: 1px solid #e2e8f0;">
            <div class="d-flex align-items-center mb-3">
                <div class="bg-primary text-white p-2 rounded-3 me-3"><i class="fa-solid fa-comments fs-4"></i></div>
                <h4 class="fw-bold mb-0 text-dark">Obieg Dokumentów i Komunikacja</h4>
            </div>

            <div class="row g-4 align-items-start">
                <div class="col-md-4">
                    <label class="fw-bold text-secondary small text-uppercase mb-2">Obecny Status Sylabusa</label>
                    <div class="p-3 border rounded bg-white fw-bold shadow-sm text-center text-primary fs-5 border-primary mb-3">
                        {% if przedmiot %}{{ przedmiot.get_status_display }}{% else %}Nowy Przedmiot{% endif %}
                    </div>
                </div>

                <div class="col-md-8">
                    <label class="fw-bold text-primary small text-uppercase mb-2">Historia Komentarzy (Czat z Prowadzącym)</label>
                    <div class="border rounded bg-white shadow-sm d-flex flex-column" style="height: 350px;">
                        <div class="p-3 flex-grow-1 overflow-auto" style="background-color: #f1f5f9;">
                            {% for kom in przedmiot.komentarze.all|default:'' %}
                                <div class="mb-3 {% if kom.autor == request.user %}text-end{% endif %}">
                                    <div class="small text-muted mb-1">{{ kom.autor.first_name }} {{ kom.autor.last_name }} <span style="font-size: 0.7rem;">({{ kom.data_utworzenia|date:"d.m.Y H:i" }})</span></div>
                                    <div class="d-inline-block p-2 rounded-3 shadow-sm {% if kom.autor == request.user %}bg-primary text-white{% else %}bg-white border{% endif %}" style="max-width: 85%; text-align: left;">
                                        {{ kom.tresc|linebreaksbr }}
                                    </div>
                                </div>
                            {% empty %}
                                <div class="text-center text-muted mt-5 pt-4 small"><i class="fa-regular fa-comment-dots fs-2 mb-2 opacity-50"></i><br>Brak wiadomości w historii. Dodaj komentarz, aby rozpocząć obieg.</div>
                            {% endfor %}
                        </div>
                        <form method="post" class="p-2 bg-white border-top d-flex gap-2">
                            {% csrf_token %}
                            <input type="text" name="tresc_komentarza" class="form-control form-control-sm" placeholder="Napisz instrukcje lub uwagi dla wykładowcy..." required>
                            <button type="submit" name="dodaj_komentarz" class="btn btn-primary btn-sm px-3 fw-bold"><i class="fa-solid fa-paper-plane"></i></button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <form method="post" id="przedmiot-form">
            {% csrf_token %}
            <div class="d-none">{{ form.status }}</div>

            <div class="row g-3 mb-4">
                <div class="col-md-5"><span class="section-label text-muted">Kierunek Studiów</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.kierunek }}</div></div>
                <div class="col-md-3"><span class="section-label text-muted">Semestr</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.semestr }}</div></div>
                <div class="col-md-4"><span class="section-label text-danger">Typ zajęć</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.typ_zajec }}</div></div>
            </div>

            <div class="p-4 rounded-3 mb-4 border bg-light shadow-sm">
                <div class="row g-3">
                    <div class="col-md-9"><span class="section-label text-muted">Nazwa PL</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.nazwa_pl }}</div></div>
                    <div class="col-md-3"><span class="section-label text-muted">Kod przedmiotu</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.kod_przedmiotu }}</div></div>
                    <div class="col-md-6"><span class="section-label text-muted">Nazwa EN</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.nazwa_en }}</div></div>
                    <div class="col-md-3"><span class="section-label text-primary fw-bold">Punkty ECTS</span><div class="field-editable rounded">{{ form.ects }}</div></div>
                    <div class="col-md-4"><span class="section-label text-muted">Język wykładowy</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.jezyk_wykladowy }}</div></div>
                    <div class="col-md-4"><span class="section-label text-muted">Cykl dydaktyczny</span><div class="{% if not is_dean %}pe-none field-locked{% endif %} rounded">{{ form.cykl_dydaktyczny }}</div></div>
                    <div class="col-md-4 d-flex align-items-end pb-1"><div class="form-check form-switch p-2 rounded border bg-white w-100 ps-5">{{ form.badania_naukowe }} <label class="fw-bold small ms-1 text-secondary">Badania naukowe?</label></div></div>
                </div>
            </div>

            <h5 class="fw-bold text-dark mt-4 mb-3"><i class="fa-regular fa-clock me-2 text-primary"></i>Rozkład Godzinowy</h5>
            <div class="row row-cols-2 row-cols-md-6 g-2 text-center mb-5">
                <div class="col"><span class="section-label">Wykład</span><div class="field-editable rounded">{{ form.godz_wyklad }}</div></div>
                <div class="col"><span class="section-label">Ćwicz.</span><div class="field-editable rounded">{{ form.godz_cwiczenia }}</div></div>
                <div class="col"><span class="section-label">Lab.</span><div class="field-editable rounded">{{ form.godz_lab }}</div></div>
                <div class="col"><span class="section-label">Proj.</span><div class="field-editable rounded">{{ form.godz_projekt }}</div></div>
                <div class="col"><span class="section-label">Sem.</span><div class="field-editable rounded">{{ form.godz_seminarium }}</div></div>
                <div class="col"><span class="section-label text-danger">Egz.</span><div class="field-editable rounded">{{ form.godz_egzamin }}</div></div>
            </div>

            <div class="row mb-5 g-4 border-top pt-4">
                <div class="col-md-5">
                    <h5 class="fw-bold text-success mb-2"><i class="fa-solid fa-users-gear me-2"></i>Obsada przedmiotu</h5>
                    <div class="p-3 border rounded bg-white shadow-sm field-editable" style="max-height: 250px; overflow-y: auto;">{{ form.koordynatorzy }}</div>
                </div>
                <div class="col-md-7">
                    <h5 class="fw-bold text-secondary mb-2"><i class="fa-solid fa-list-check me-2"></i>Aktualne Efekty Przedmiotu</h5>
                    <div class="p-3 border rounded bg-light shadow-sm" style="max-height: 250px; overflow-y: auto;">
                        {% if przedmiot and przedmiot.efekty_kierunkowe.all %}
                            <ul class="list-group list-group-flush small">
                                {% for e in przedmiot.efekty_kierunkowe.all %}
                                    <li class="list-group-item bg-transparent px-0 py-1 d-flex justify-content-between align-items-center">
                                        <div><strong class="text-dark">{{ e.kod }}</strong>: <span class="text-muted">{{ e.opis }}</span></div>
                                        <div class="form-check m-0 ms-2"><input class="form-check-input" type="checkbox" name="usun_efekt" value="{{ e.id }}"></div>
                                    </li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <p class="text-center text-muted my-3 small">Brak przypisanych efektów.</p>
                        {% endif %}
                    </div>
                </div>
            </div>

            <h5 class="fw-bold text-danger mb-2"><i class="fa-solid fa-plus-circle me-2"></i>Dodaj nowe Efekty</h5>
            <div class="p-3 bg-white border rounded shadow-sm mb-4 field-editable">
                <div id="nowe-efekty-container">
                    <div class="row g-2 mb-2 align-items-center efekt-row pb-2">
                        <div class="col-md-3"><select name="nowy_efekt_kat" class="form-select border-primary"><option value="W">Wiedza (W)</option><option value="U">Umiejętności (U)</option><option value="K">Kompetencje (K)</option></select></div>
                        <div class="col-md-8"><input type="text" name="nowy_efekt_opis" class="form-control border-primary" placeholder="Treść nowego efektu..."></div>
                        <div class="col-md-1 text-center"><button type="button" class="btn btn-outline-secondary" onclick="this.closest('.efekt-row').remove()"><i class="fa-solid fa-xmark"></i></button></div>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-danger fw-bold mt-2 shadow-sm" onclick="addEfektRow()"><i class="fa-solid fa-plus me-1"></i> Dodaj kolejny wiersz</button>
            </div>

            <div class="mt-5 d-flex justify-content-between border-top pt-4">
                <a href="/" class="btn btn-outline-secondary px-4 btn-lg">Anuluj</a>
                <div class="d-flex gap-2">
                    {% if przedmiot %}
                        <button type="button" class="btn btn-danger btn-lg shadow-sm fw-bold" onclick="zmienStatus('DO_POPRAWY')"><i class="fa-solid fa-rotate-left me-2"></i>Cofnij do poprawy</button>
                        {% if is_dean %}
                            <button type="button" class="btn btn-success btn-lg shadow-sm fw-bold" onclick="zmienStatus('ZATWIERDZONY')"><i class="fa-solid fa-check-double me-2"></i>Zatwierdź Ostatecznie</button>
                        {% else %}
                            <button type="button" class="btn btn-success btn-lg shadow-sm fw-bold" onclick="zmienStatus('SPRAWDZONY')"><i class="fa-solid fa-check me-2"></i>Oznacz jako Sprawdzony</button>
                        {% endif %}
                    {% endif %}
                    <button type="submit" class="btn btn-primary btn-lg px-4 shadow-sm fw-bold"><i class="fa-solid fa-floppy-disk me-2"></i>Zapisz</button>
                </div>
            </div>
        </form>
    </div>
</div>

<script>
    function addEfektRow() {
        const container = document.getElementById('nowe-efekty-container');
        const row = document.createElement('div');
        row.className = 'row g-2 mb-2 align-items-center efekt-row pb-2 border-top pt-2';
        row.innerHTML = `<div class="col-md-3"><select name="nowy_efekt_kat" class="form-select border-primary"><option value="W">Wiedza (W)</option><option value="U">Umiejętności (U)</option><option value="K">Kompetencje (K)</option></select></div><div class="col-md-8"><input type="text" name="nowy_efekt_opis" class="form-control border-primary" placeholder="Treść efektu..."></div><div class="col-md-1 text-center"><button type="button" class="btn btn-outline-danger" onclick="this.closest('.efekt-row').remove()"><i class="fa-solid fa-xmark"></i></button></div>`;
        container.appendChild(row);
    }
    function zmienStatus(nowyStatus) {
        document.getElementById('id_status').value = nowyStatus;
        document.getElementById('przedmiot-form').submit();
    }
</script>
{% endblock %}
"""

# ==========================================
# 7. CZAT W EDYCJA_SYLABUSA.HTML (CZESCIOWA PODMIANA)
# ==========================================
edycja_html = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Edycja Sylabusa: {{ przedmiot.nazwa_pl }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary-color: #2563eb; --primary-light: #eff6ff; --secondary-color: #475569; --border-color: #e2e8f0; --bg-gradient: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%); --card-bg: #ffffff; --success-color: #16a34a; --danger-color: #dc2626; --font-family: 'Inter', sans-serif; }
        body { background: var(--bg-gradient); background-attachment: fixed; font-family: var(--font-family); color: #334155; line-height: 1.6; min-height: 100vh; }
        .page-header { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 2.5rem 0; margin-bottom: 2.5rem; box-shadow: 0 4px 20px rgba(30, 58, 138, 0.15); color: white; }
        .subject-title { font-weight: 700; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 0.8rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .badge-custom { font-weight: 500; padding: 0.5em 0.8em; border-radius: 6px; font-size: 0.85rem; background: rgba(255, 255, 255, 0.15); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.3); backdrop-filter: blur(4px); }
        .editor-container { max-width: 1200px; margin: 0 auto; padding: 0 15px; }
        .section-card { border: none; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); margin-bottom: 2.5rem; border-radius: 12px; background-color: var(--card-bg); overflow: hidden; transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .section-card:hover { transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
        .section-header { padding: 1.2rem 1.5rem; font-weight: 600; color: #ffffff; display: flex; align-items: center; font-size: 1.15rem; letter-spacing: 0.02em; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .header-blue   { background: linear-gradient(135deg, #1d4ed8 0%, #60a5fa 100%); }
        .header-green  { background: linear-gradient(135deg, #237a57 0%, #5cb892 100%); }
        .header-orange { background: linear-gradient(135deg, #bd5d2a 0%, #e68d60 100%); }
        .header-purple { background: linear-gradient(135deg, #5b4d82 0%, #8c7eb6 100%); }
        .header-slate  { background: linear-gradient(135deg, #3f4e60 0%, #8393a7 100%); }
        .section-icon { margin-right: 12px; color: #ffffff; width: 28px; text-align: center; font-size: 1.25rem; opacity: 0.9; }
        .card-body { padding: 2.5rem; }
        label { font-weight: 600; color: var(--secondary-color); margin-top: 1rem; margin-bottom: 0.5rem; display: block; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .form-control, .form-select { border: 1px solid #cbd5e1; border-radius: 6px; padding: 0.6rem 0.8rem; font-size: 0.95rem; transition: all 0.2s; background-color: #f8fafc; }
        .form-control:focus, .form-select:focus { background-color: #fff; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); border-color: var(--primary-color); }
        .manager-col { background: #ffffff; border: 1px solid var(--border-color); border-radius: 10px; padding: 1.5rem; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; overflow: hidden; }
        .manager-col::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
        .manager-col.border-w::before { background: #3b82f6; }
        .manager-col.border-u::before { background: #5cb892; }
        .manager-col.border-k::before { background: #e68d60; }
        .manager-header { font-size: 1rem; color: #1e293b; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem; text-align: center; text-transform: uppercase; letter-spacing: 0.05em; }
        .cel-item { display: flex; align-items: flex-start; margin-bottom: 0.75rem; background: #f8fafc; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.5rem; transition: border-color 0.2s; }
        .cel-item:focus-within { border-color: var(--primary-color); background: #fff;}
        .cel-badge { background-color: var(--primary-light); color: var(--primary-color); border: 1px solid #bfdbfe; margin-top: 0.2rem; margin-right: 0.75rem; padding: 0.35em 0.65em; font-weight: 600; }
        .checkbox-container { border: 1px solid var(--border-color); border-radius: 8px; max-height: 400px; overflow-y: auto; background: #fff; box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02); }
        #id_efekty_kierunkowe { list-style: none; padding: 0; margin: 0; }
        #id_efekty_kierunkowe li { border-bottom: 1px solid var(--border-color); padding: 0.9rem 1.2rem; display: flex; align-items: center; transition: background-color 0.2s; }
        #id_efekty_kierunkowe li:last-child { border-bottom: none; }
        #id_efekty_kierunkowe li:hover { background: var(--primary-light); }
        #id_efekty_kierunkowe label { font-weight: 500; margin: 0; cursor: pointer; font-size: 0.95rem; color: #1e293b; text-transform: none; letter-spacing: normal; }
        #id_efekty_kierunkowe input[type="checkbox"] { margin-right: 1.2rem; transform: scale(1.3); cursor: pointer; accent-color: var(--primary-color); }
        .harm-group { border: 1px solid var(--border-color); border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; background: #f8fafc; position: relative; border-left: 4px solid #d27346; }
        .harm-group-delete { position: absolute; top: 1rem; right: 1rem; color: #94a3b8; background: white; border: 1px solid var(--border-color); border-radius: 4px; padding: 4px 8px; transition: all 0.2s; }
        .harm-group-delete:hover { color: white; background: var(--danger-color); border-color: var(--danger-color); }
        .harm-topic-row { display: flex; align-items: center; margin-bottom: 0.5rem; }
        .harm-topic-number { width: 30px; text-align: right; margin-right: 12px; color: #64748b; font-weight: 600; font-size: 0.9rem; }
        .hours-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding: 1.2rem 0; }
        .hours-row:last-child { border-bottom: none; }
        .hours-row span { font-weight: 500; color: #334155; }
        .hours-row input { text-align: right; width: 100px; font-weight: bold; color: var(--primary-color);}
        .btn { font-weight: 600; padding: 0.5rem 1.2rem; border-radius: 8px; transition: all 0.2s; }
        .btn-outline-light:hover { color: #1e3a8a; }
        .btn-outline-primary { color: var(--primary-color); border-color: var(--primary-color); border-width: 2px;}
        .btn-outline-primary:hover { background-color: var(--primary-light); color: var(--primary-color); }
        .btn-action-small { padding: 0.25rem 0.5rem; font-size: 0.875rem; border-radius: 6px; }
        .action-bar { background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-top: 1px solid var(--border-color); padding: 1.2rem 0; box-shadow: 0 -10px 15px -3px rgba(0, 0, 0, 0.05); }
        .status-indicator { display: flex; align-items: center; color: var(--secondary-color); font-weight: 500; }
        .status-dot { width: 10px; height: 10px; background-color: var(--success-color); border-radius: 50%; margin-right: 10px; box-shadow: 0 0 0 3px #dcfce7; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); } 70% { box-shadow: 0 0 0 6px rgba(22, 163, 74, 0); } 100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); } }
    </style>
</head>
<body>

<div class="page-header">
    <div class="editor-container d-flex justify-content-between align-items-center">
        <div>
            <h1 class="subject-title">{{ przedmiot.nazwa_pl }}</h1>
            <div class="d-flex gap-2 align-items-center mt-3">
                <span class="badge-custom" style="background: rgba(255, 255, 255, 0.25); border-color: rgba(255, 255, 255, 0.6); font-weight: 600;">
                    <i class="fa-solid fa-graduation-cap me-1 opacity-100"></i>
                    {% if przedmiot.modul.kierunek %}{{ przedmiot.modul.kierunek }}{% else %}Brak kierunku{% endif %}
                </span>
                <span class="badge-custom"><i class="fa-solid fa-hashtag me-1 opacity-75"></i> {{ przedmiot.kod_przedmiotu }}</span>
                <span class="badge-custom"><i class="fa-solid fa-star me-1 text-warning"></i> ECTS: {{ przedmiot.ects }}</span>
                <span class="badge-custom"><i class="fa-regular fa-calendar me-1 opacity-75"></i> Semestr {{ przedmiot.modul.semestr }} ({{ przedmiot.cykl_dydaktyczny }})</span>
            </div>
        </div>
        <a href="/" class="btn btn-outline-light"><i class="fa-solid fa-arrow-left me-2"></i> Powrót do kokpitu</a>
    </div>
</div>

<div class="container editor-container mb-5">

    <div class="row mb-5">
        <div class="col-12">
            <div class="card shadow-sm border-0 rounded-4 overflow-hidden">
                <div class="card-header bg-primary text-white p-3 fw-bold d-flex align-items-center">
                    <i class="fa-solid fa-comments fs-5 me-2"></i> Konwersacja z Koordynatorami (Obecny status: {{ przedmiot.get_status_display }})
                </div>
                <div class="card-body p-0 bg-light">
                    <div class="d-flex flex-column" style="height: 250px;">
                        <div class="p-3 flex-grow-1 overflow-auto">
                            {% for kom in przedmiot.komentarze.all|default:'' %}
                                <div class="mb-3 {% if kom.autor == request.user %}text-end{% endif %}">
                                    <div class="small text-muted mb-1">{{ kom.autor.first_name }} {{ kom.autor.last_name }} <span style="font-size: 0.7rem;">({{ kom.data_utworzenia|date:"d.m.Y H:i" }})</span></div>
                                    <div class="d-inline-block p-2 rounded-3 shadow-sm {% if kom.autor == request.user %}bg-primary text-white{% else %}bg-white border{% endif %}" style="max-width: 85%; text-align: left;">
                                        {{ kom.tresc|linebreaksbr }}
                                    </div>
                                </div>
                            {% empty %}
                                <div class="text-center text-muted mt-4 small"><i class="fa-regular fa-comment-dots fs-2 mb-2 opacity-50"></i><br>Brak wiadomości. Tutaj zobaczysz uwagi, jeśli Twój sylabus zostanie cofnięty.</div>
                            {% endfor %}
                        </div>
                        <form method="post" class="p-3 bg-white border-top d-flex gap-2">
                            {% csrf_token %}
                            <input type="text" name="tresc_komentarza" class="form-control form-control-sm" placeholder="Odpowiedz koordynatorowi..." required>
                            <button type="submit" name="dodaj_komentarz" class="btn btn-primary btn-sm px-3 fw-bold"><i class="fa-solid fa-paper-plane"></i></button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {% if form.errors %}
    <div class="alert alert-danger shadow-sm border-0 border-start border-danger border-4 mb-4 bg-white">
        <h5 class="alert-heading fw-bold mb-1 text-danger"><i class="fa-solid fa-circle-exclamation me-2"></i>Wystąpił błąd podczas zapisu</h5>
        <div class="small text-muted">{{ form.errors }}</div>
    </div>
    {% endif %}

    <form method="post">
        {% csrf_token %}

        <div class="card section-card">
            <div class="section-header header-blue">
                <span class="section-icon"><i class="fa-solid fa-circle-info"></i></span>
                1. Informacje Podstawowe i Cele Przedmiotu
            </div>
            <div class="card-body">
                <div class="mb-5">
                    <label>Wymagania wstępne</label>
                    {{ form.wymagania_wstepne }}
                </div>

                <div style="display:none;">{{ form.opis_wstepny }}</div>

                <div class="d-flex align-items-center mb-4 mt-5">
                    <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-bullseye me-2 text-primary"></i> Cele Kształcenia i Metody Weryfikacji</h5>
                    <span class="ms-3 text-muted small">(Podział na kategorie)</span>
                </div>

                <div class="row g-4 mt-2">
                    <div class="col-md-4">
                        <div class="manager-col border-w">
                            <h6 class="manager-header fw-bold"><i class="fa-solid fa-brain text-primary fs-5"></i><br>Wiedza (W)</h6>
                            <div id="cele-list-W" class="mb-3"></div>
                            <button type="button" class="btn btn-sm btn-outline-primary w-100" onclick="window.addCel('W')"><i class="fa-solid fa-plus me-1"></i> Dodaj cel</button>
                            <hr class="my-4 text-muted">
                            <label class="small fw-bold text-secondary mb-2">Metoda weryfikacji (Wiedza):</label>
                            <input type="text" id="metoda-W" class="form-control form-control-sm" placeholder="np. Egzamin pisemny" oninput="window.updateMetoda('W', this.value)">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="manager-col border-u">
                            <h6 class="manager-header fw-bold"><i class="fa-solid fa-wrench fs-5" style="color: #237a57;"></i><br>Umiejętności (U)</h6>
                            <div id="cele-list-U" class="mb-3"></div>
                            <button type="button" class="btn btn-sm w-100" style="color: #237a57; border-color: #237a57; border-width: 2px;" onclick="window.addCel('U')" onmouseover="this.style.backgroundColor='#ecfdf5'" onmouseout="this.style.backgroundColor='transparent'"><i class="fa-solid fa-plus me-1"></i> Dodaj cel</button>
                            <hr class="my-4 text-muted">
                            <label class="small fw-bold text-secondary mb-2">Metoda weryfikacji (Umiejętności):</label>
                            <input type="text" id="metoda-U" class="form-control form-control-sm" placeholder="np. Wykonanie ćwiczenia" oninput="window.updateMetoda('U', this.value)">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="manager-col border-k">
                            <h6 class="manager-header fw-bold"><i class="fa-solid fa-users fs-5" style="color: #bd5d2a;"></i><br>Kompetencje (K)</h6>
                            <div id="cele-list-K" class="mb-3"></div>
                            <button type="button" class="btn btn-sm w-100" style="color: #bd5d2a; border-color: #bd5d2a; border-width: 2px;" onclick="window.addCel('K')" onmouseover="this.style.backgroundColor='#fff7ed'" onmouseout="this.style.backgroundColor='transparent'"><i class="fa-solid fa-plus me-1"></i> Dodaj cel</button>
                            <hr class="my-4 text-muted">
                            <label class="small fw-bold text-secondary mb-2">Metoda weryfikacji (Kompetencje):</label>
                            <input type="text" id="metoda-K" class="form-control form-control-sm" placeholder="np. Udział w dyskusji" oninput="window.updateMetoda('K', this.value)">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card section-card">
            <div class="section-header header-green">
                <span class="section-icon"><i class="fa-solid fa-table-cells"></i></span>
                2. Efekty Uczenia się (Matryca)
            </div>
            <div class="card-body">
                <div class="d-flex p-3 rounded mb-4" style="background-color: #f1f8f5; border: 1px solid #bce3d1;">
                    <div class="me-3 mt-1" style="color: #237a57;"><i class="fa-solid fa-circle-info fs-5"></i></div>
                    <div class="small text-dark"><strong>Instrukcja:</strong> Zaznacz efekty kierunkowe z listy poniżej. Zostaną one automatycznie powiązane z celami dodanymi w poprzedniej sekcji podczas generowania dokumentu.</div>
                </div>

                <label class="mb-2">Dostępne Efekty Kierunkowe</label>
                <div class="checkbox-container">
                    {{ form.efekty_kierunkowe }}
                </div>

                <div style="display:none;">{{ form.efekty_wiedza }}{{ form.efekty_umiejetnosci }}{{ form.efekty_kompetencje }}{{ form.mapowanie_efektow }}</div>
            </div>
        </div>

        <div class="card section-card">
            <div class="section-header header-orange">
                <span class="section-icon"><i class="fa-solid fa-calendar-days"></i></span>
                3. Harmonogram Realizacji Zajęć
            </div>
            <div class="card-body">
                <div class="row g-5">
                    <div class="col-12">
                        <div style="display:none;">{{ form.harmonogram_raw }}</div>

                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <label class="mt-0 mb-0 text-dark">Zarządzanie blokami tematycznymi</label>
                            <div class="text-muted small bg-light px-3 py-2 rounded border border-warning shadow-sm">
                                <strong><i class="fa-solid fa-hourglass-half me-1"></i> Twój budżet (h):</strong>
                                <span class="ms-1">W({{ przedmiot.godz_wyklad }})</span> |
                                <span>Ć({{ przedmiot.godz_cwiczenia }})</span> |
                                <span>L({{ przedmiot.godz_lab }})</span> |
                                <span>P({{ przedmiot.godz_projekt }})</span>
                            </div>
                        </div>

                        <div id="harmonogram-ui-container"></div>

                        <button type="button" class="btn btn-outline-secondary text-dark w-100 mt-2 border-dashed" style="border-style: dashed;" onclick="window.addHarmGroup()">
                            <i class="fa-solid fa-plus me-2"></i>Dodaj nową grupę zajęć (np. kolejny wykład)
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="card section-card">
            <div class="section-header header-purple">
                <span class="section-icon"><i class="fa-solid fa-clock"></i></span>
                4. Obciążenie pracą studenta i ECTS
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-7 border-end pe-4">

                        <div class="mb-4 p-3 bg-light border rounded-3 border-start border-primary border-4 shadow-sm">
                            <div class="d-flex align-items-center mb-2">
                                <i class="fa-solid fa-lock text-primary fs-6 me-2"></i>
                                <h6 class="fw-bold text-dark mb-0 small text-uppercase">Godziny przydzielone (Zablokowane)</h6>
                            </div>
                            <div class="d-flex flex-wrap gap-2 small">
                                <span class="badge bg-white text-dark border shadow-sm">Wykład: {{ przedmiot.godz_wyklad }}h</span>
                                <span class="badge bg-white text-dark border shadow-sm">Ćwiczenia: {{ przedmiot.godz_cwiczenia }}h</span>
                                <span class="badge bg-white text-dark border shadow-sm">Laboratorium: {{ przedmiot.godz_lab }}h</span>
                                <span class="badge bg-white text-dark border shadow-sm">Projekt: {{ przedmiot.godz_projekt }}h</span>
                                <span class="badge bg-white text-dark border shadow-sm">Seminarium: {{ przedmiot.godz_seminarium }}h</span>
                            </div>
                            <div class="mt-2 text-muted" style="font-size: 0.75rem;">
                                * Tych godzin nie możesz zmienić. Są one podstawą do wyliczenia pracy własnej studenta poniżej.
                            </div>
                        </div>

                        <div class="d-flex align-items-center mb-3 mt-4">
                            <i class="fa-solid fa-user-graduate text-secondary fs-5 me-2"></i>
                            <h6 class="fw-bold text-secondary mb-0">Praca własna studenta (Do uzupełnienia)</h6>
                        </div>
                        <div class="hours-row"><span>Przygotowanie do ćwiczeń:</span> {{ form.pw_przygotowanie_cw }}</div>
                        <div class="hours-row"><span>Sprawozdania/Laboratoria:</span> {{ form.pw_sprawozdania }}</div>
                        <div class="hours-row"><span>Przygotowanie projektu:</span> {{ form.pw_projekt }}</div>
                        <div class="hours-row"><span>Nauka do wykładu/zaliczenia:</span> {{ form.pw_wyklad }}</div>
                        <div class="hours-row"><span>Przygotowanie do egzaminu:</span> {{ form.pw_egzamin }}</div>
                        <div class="hours-row border-0"><span>Studiowanie literatury:</span> {{ form.pw_literatura }}</div>
                    </div>

                    <div class="col-md-5 ps-4">
                        <div class="p-3 rounded h-100" style="background-color: #f8fafc; border: 2px dashed #cbd5e1;">
                            <h6 class="fw-bold text-center mb-4"><i class="fa-solid fa-calculator text-primary me-2"></i>Kalkulator ECTS (Live)</h6>

                            <div class="d-flex justify-content-between mb-2 small text-muted">
                                <span>Kontakt z prowadzącym (stałe):</span>
                                <strong id="live-kontaktowe" class="text-dark">0 h</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-2 small text-muted">
                                <span>Praca własna (suma):</span>
                                <strong id="live-wlasna" class="text-dark">0 h</strong>
                            </div>
                            <hr class="text-muted opacity-25">
                            <div class="d-flex justify-content-between mb-1">
                                <span class="fw-bold">Całkowity czas pracy:</span>
                                <strong id="live-suma" class="fs-5">0 h</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-4 small">
                                <span class="text-muted">Wymagane dla <b class="text-dark">{{ przedmiot.ects }} ECTS</b>:</span>
                                <strong id="live-wymagane" class="text-primary">0 h</strong>
                            </div>

                            <div id="alert-ects" class="alert alert-danger py-2 px-3 small mb-2 shadow-sm" style="display: none; border-left: 4px solid #dc2626;">
                                <i class="fa-solid fa-triangle-exclamation me-1"></i> Błąd sumy! Brakuje lub masz za dużo godzin w stosunku do punktów ECTS.
                            </div>
                            <div id="alert-proporcja" class="alert alert-warning py-2 px-3 small mb-2 shadow-sm" style="display: none; border-left: 4px solid #ca8a04;">
                                <i class="fa-solid fa-scale-unbalanced me-1"></i> Poniżej 50% godzin w kontakcie z prowadzącym.
                            </div>
                            <div id="alert-ok" class="alert alert-success py-2 px-3 small mb-0 shadow-sm" style="display: none; border-left: 4px solid #16a34a;">
                                <i class="fa-solid fa-check-circle me-1"></i> Parametry godzinowe są poprawne.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card section-card">
            <div class="section-header header-slate">
                <span class="section-icon"><i class="fa-solid fa-book-open"></i></span>
                5. Metodyka, Organizacja i Literatura
            </div>
            <div class="card-body">
                <div class="row g-4 mb-2">
                    <div class="col-md-6">
                        <label>Metody nauczania</label>
                        {{ form.metody_nauczania }}
                    </div>
                    <div class="col-md-6">
                        <label>Formy oceny (opis ogólny)</label>
                        {{ form.formy_oceny }}
                    </div>
                </div>

                <label>Szczegółowe zasady oceniania</label>
                {{ form.zasady_oceniania }}

                <div class="row g-4 mb-2">
                    <div class="col-md-6">
                        <label>Zasady odrabiania zajęć</label>
                        {{ form.odrabianie_zajec }}
                    </div>
                    <div class="col-md-6">
                        <label>Wymagania dotyczące obecności</label>
                        {{ form.wymagania_obecnosci }}
                    </div>
                </div>

                <div class="row g-4 mt-4">
                    <div class="col-12">
                        <h6 class="fw-bold text-dark border-bottom pb-2 mb-3"><i class="fa-solid fa-book text-primary me-2"></i>Wykaz Literatury</h6>
                        {{ form.literatura }}
                    </div>
                </div>
            </div>
        </div>

        <div class="fixed-bottom action-bar z-3">
            <div class="container editor-container d-flex justify-content-between align-items-center">
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>Tryb edycji aktywny</span>
                </div>
                <div class="d-flex gap-3">
                    <a href="/" class="btn btn-outline-secondary px-4">Anuluj</a>
                    <a href="/pdf/{{ przedmiot.id }}/" class="btn btn-outline-danger px-4" target="_blank"><i class="fa-solid fa-file-pdf me-2"></i>PDF</a>

                    <button type="submit" name="zapisz_roboczy" class="btn btn-outline-primary px-4 shadow-sm bg-white"><i class="fa-solid fa-floppy-disk me-2"></i>Zapisz szkic</button>
                    <button type="submit" name="przekaz_dalej" class="btn btn-success px-5 shadow-sm fw-bold"><i class="fa-solid fa-paper-plane me-2"></i>Przekaż do sprawdzenia</button>
                </div>
            </div>
        </div>

        <div style="height: 120px;"></div>
    </form>
</div>

<script>
    document.addEventListener("DOMContentLoaded", function() {
        const fieldCele = document.getElementById("id_opis_wstepny");
        let celeList = [];
        let metodyDict = { W: '', U: '', K: '' };

        function parseCeleData() {
            const raw = fieldCele.value.trim();
            celeList = [];
            metodyDict = { W: '', U: '', K: '' };
            if (!raw) return;

            let mode = 'cele';
            raw.split('\\n').forEach(line => {
                line = line.trim();
                if (!line) return;
                if (line === '---METODY---') { mode = 'metody'; return; }

                let parts = line.split('|');
                if (mode === 'cele' && parts.length >= 3) {
                    celeList.push({ kategoria: parts[0].trim(), tresc: parts[2].trim() });
                } else if (mode === 'metody' && parts.length >= 2) {
                    metodyDict[parts[0].trim()] = parts[1].trim();
                }
            });
        }

        function saveCeleData() {
            let lines = [];
            let counter = 1;
            celeList.forEach(c => {
                lines.push(`${c.kategoria} | O${counter} | ${c.tresc}`);
                counter++;
            });
            lines.push('---METODY---');
            for (const [kat, val] of Object.entries(metodyDict)) {
                if (val.trim()) lines.push(`${kat} | ${val.trim()}`);
            }
            fieldCele.value = lines.join('\\n');
        }

        function renderCeleUI() {
            document.getElementById('cele-list-W').innerHTML = '';
            document.getElementById('cele-list-U').innerHTML = '';
            document.getElementById('cele-list-K').innerHTML = '';

            let counter = 1;
            celeList.forEach((c, index) => {
                const kod = 'O' + counter++;
                const html = `
                    <div class="cel-item">
                        <span class="badge rounded-pill cel-badge">${kod}</span>
                        <div class="flex-grow-1">
                            <textarea class="form-control form-control-sm border-0 bg-transparent p-0" style="resize: none;" rows="2" placeholder="Wpisz treść celu..." oninput="window.updateCel(${index}, this.value)">${c.tresc}</textarea>
                        </div>
                        <button type="button" class="btn btn-action-small text-muted border-0 ms-1" onclick="window.removeCel(${index})" title="Usuń cel">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>`;
                document.getElementById('cele-list-' + c.kategoria).insertAdjacentHTML('beforeend', html);
            });

            document.getElementById('metoda-W').value = metodyDict.W || '';
            document.getElementById('metoda-U').value = metodyDict.U || '';
            document.getElementById('metoda-K').value = metodyDict.K || '';
        }

        window.addCel = function(kat) { celeList.push({ kategoria: kat, tresc: '' }); saveCeleData(); renderCeleUI(); };
        window.removeCel = function(index) { celeList.splice(index, 1); saveCeleData(); renderCeleUI(); };
        window.updateCel = function(index, value) { celeList[index].tresc = value; saveCeleData(); };
        window.updateMetoda = function(kat, value) { metodyDict[kat] = value; saveCeleData(); };

        parseCeleData();
        renderCeleUI();

        const fieldHarm = document.getElementById("id_harmonogram_raw");
        const harmContainer = document.getElementById("harmonogram-ui-container");
        let harmGroups = [];

        function parseHarmData() {
            const raw = fieldHarm.value.trim();
            harmGroups = [];
            if (!raw) {
                harmGroups.push({forma: 'wykład', efekty: '', tematy: ['']});
                return;
            }
            let currentGroup = null;
            raw.split('\\n').forEach(line => {
                line = line.trim();
                if (!line) return;
                let forma = 'wykład';
                let efekty = '';
                let tresc = line;
                if (line.startsWith('[')) {
                    let endIdx = line.indexOf(']');
                    if (endIdx !== -1) {
                        let meta = line.substring(1, endIdx);
                        tresc = line.substring(endIdx+1).trim();
                        let parts = meta.split('|');
                        forma = parts[0].trim();
                        if (parts.length > 1) efekty = parts[1].trim();
                    }
                }
                if (!currentGroup || currentGroup.forma !== forma || currentGroup.efekty !== efekty) {
                    currentGroup = { forma: forma, efekty: efekty, tematy: [] };
                    harmGroups.push(currentGroup);
                }
                currentGroup.tematy.push(tresc);
            });
            harmGroups.forEach(g => { if (g.tematy.length === 0) g.tematy.push(''); });
        }

        function saveHarmData() {
            let lines = [];
            harmGroups.forEach(g => {
                const prefix = `[${g.forma}|${g.efekty}]`;
                g.tematy.forEach(t => {
                    if(t.trim()) lines.push(`${prefix} ${t.trim()}`);
                });
            });
            fieldHarm.value = lines.join('\\n');
        }

        function renderHarmUI() {
            let html = '';
            const opcje = ['wykład', 'laboratorium', 'ćwiczenia', 'projekt', 'seminarium'];

            harmGroups.forEach((g, i) => {
                html += `
                <div class="harm-group shadow-sm">
                    <button type="button" class="harm-group-delete" onclick="window.removeHarm(${i})" title="Usuń cały blok">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>

                    <div class="row mb-4 pe-4">
                        <div class="col-md-5">
                            <label class="small mt-0 mb-1 text-muted">Rodzaj zajęć</label>
                            <select class="form-select form-select-sm" onchange="window.updateHarm(${i}, 'forma', this.value)">`;
                opcje.forEach(o => { html += `<option value="${o}" ${g.forma === o ? 'selected' : ''}>${o}</option>`; });
                html += `   </select>
                        </div>
                        <div class="col-md-7">
                            <label class="small mt-0 mb-1 text-muted">Powiązane efekty (np. W1, K1)</label>
                            <input type="text" class="form-control form-control-sm" placeholder="Opcjonalne kody efektów" value="${g.efekty}" oninput="window.updateHarm(${i}, 'efekty', this.value)">
                        </div>
                    </div>

                    <div class="mb-2 text-secondary small fw-bold"><i class="fa-solid fa-list-ul me-1"></i> Tematy realizowane w ramach bloku:</div>
                    <div id="tematy-list-${i}">`;

                g.tematy.forEach((t, tIdx) => {
                    html += `
                    <div class="harm-topic-row">
                        <span class="harm-topic-number">${tIdx + 1}.</span>
                        <input type="text" class="form-control form-control-sm harm-input-${i}" placeholder="Wprowadź temat zajęć i naciśnij Enter..." value="${t}"
                               oninput="window.updateHarmTemat(${i}, ${tIdx}, this.value)"
                               onkeydown="window.handleHarmKey(event, ${i}, ${tIdx})">
                        <button type="button" class="btn btn-action-small text-muted ms-1 border-0" tabindex="-1" onclick="window.removeHarmTemat(${i}, ${tIdx})" title="Usuń temat">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>`;
                });

                html += `<div class="mt-2 ms-4 pl-2"><button type="button" class="btn btn-sm btn-light border text-primary shadow-sm" onclick="window.addHarmTemat(${i})"><i class="fa-solid fa-plus me-1"></i> Dodaj kolejny temat do tego bloku</button></div>`;
                html += `</div></div>`;
            });
            harmContainer.innerHTML = html;
        }

        window.addHarmGroup = function() { harmGroups.push({forma: 'laboratorium', efekty: '', tematy: ['']}); saveHarmData(); renderHarmUI(); };
        window.removeHarm = function(i) { harmGroups.splice(i, 1); saveHarmData(); renderHarmUI(); };
        window.updateHarm = function(i, pole, val) { harmGroups[i][pole] = val; saveHarmData(); };
        window.updateHarmTemat = function(gIdx, tIdx, val) { harmGroups[gIdx].tematy[tIdx] = val; saveHarmData(); };
        window.removeHarmTemat = function(gIdx, tIdx) {
            harmGroups[gIdx].tematy.splice(tIdx, 1);
            if(harmGroups[gIdx].tematy.length === 0) harmGroups[gIdx].tematy.push('');
            saveHarmData(); renderHarmUI();
        };

        window.addHarmTemat = function(gIdx) {
            harmGroups[gIdx].tematy.push('');
            saveHarmData(); renderHarmUI();
            setTimeout(() => {
                const inputs = document.querySelectorAll(`.harm-input-${gIdx}`);
                if (inputs.length > 0) inputs[inputs.length - 1].focus();
            }, 50);
        };

        window.handleHarmKey = function(e, gIdx, tIdx) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (tIdx === harmGroups[gIdx].tematy.length - 1) { window.addHarmTemat(gIdx); }
                else { const inputs = document.querySelectorAll(`.harm-input-${gIdx}`); if (inputs[tIdx + 1]) inputs[tIdx + 1].focus(); }
            }
        };

        parseHarmData();
        renderHarmUI();

        const ects = parseInt('{{ przedmiot.ects|default:"0" }}') || 0;
        const h_wyk = parseInt('{{ przedmiot.godz_wyklad|default:"0" }}') || 0;
        const h_cw = parseInt('{{ przedmiot.godz_cwiczenia|default:"0" }}') || 0;
        const h_lab = parseInt('{{ przedmiot.godz_lab|default:"0" }}') || 0;
        const h_proj = parseInt('{{ przedmiot.godz_projekt|default:"0" }}') || 0;
        const h_sem = parseInt('{{ przedmiot.godz_seminarium|default:"0" }}') || 0;

        const allInputs = [
            document.getElementById('id_pw_przygotowanie_cw'), document.getElementById('id_pw_sprawozdania'),
            document.getElementById('id_pw_projekt'), document.getElementById('id_pw_wyklad'),
            document.getElementById('id_pw_egzamin'), document.getElementById('id_pw_literatura')
        ];

        function calculateECTS() {
            let egzamin_kontakt = (parseInt(document.getElementById('id_pw_egzamin')?.value) || 0) > 0 ? 2 : 0;
            const sumaKontaktowe = h_wyk + h_cw + h_lab + h_proj + h_sem + egzamin_kontakt;
            let sumaWlasna = 0;
            allInputs.forEach(input => { if (input) sumaWlasna += parseInt(input.value) || 0; });
            const sumaCalkowita = sumaKontaktowe + sumaWlasna;
            const wymaganeGodziny = ects * 25;

            document.getElementById('live-kontaktowe').textContent = sumaKontaktowe + ' h';
            document.getElementById('live-wlasna').textContent = sumaWlasna + ' h';
            document.getElementById('live-suma').textContent = sumaCalkowita + ' h';
            document.getElementById('live-wymagane').textContent = wymaganeGodziny + ' h (25h/ECTS)';

            let isError = Math.abs(sumaCalkowita - wymaganeGodziny) > 2;
            document.getElementById('alert-ects').style.display = isError ? 'block' : 'none';
            document.getElementById('live-suma').className = isError ? "fs-5 text-danger" : "fs-5 text-success";

            let showProporcjaWarning = sumaCalkowita > 0 && (sumaKontaktowe / sumaCalkowita) <= 0.5;
            document.getElementById('alert-proporcja').style.display = showProporcjaWarning ? 'block' : 'none';
            document.getElementById('alert-ok').style.display = (!isError && !showProporcjaWarning && sumaCalkowita > 0) ? 'block' : 'none';
        }

        allInputs.forEach(input => { if (input) input.addEventListener('input', calculateECTS); });
        calculateECTS();
    });
</script>
</body>
</html>
"""

zapisz("core/models.py", models)
zapisz("core/forms.py", forms_py)
zapisz("core/views.py", views_py)
zapisz("core/urls.py", urls_py)
zapisz("core/templates/core/panel_zarzadzania.html", panel_html)
zapisz("core/templates/core/formularz_przedmiotu.html", form_html)
zapisz("core/templates/core/edycja_sylabusa.html", edycja_html)