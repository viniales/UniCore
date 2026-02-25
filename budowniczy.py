import os

def zapisz(sciezka, tresc):
    os.makedirs(os.path.dirname(sciezka) if os.path.dirname(sciezka) else ".", exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as f:
        f.write(tresc.strip())
    print(f"✅ Plik gotowy: {sciezka}")

# --- PENY MODELS.PY ---
models = """from django.db import models
from django.contrib.auth.models import User

class EfektUczenia(models.Model):
    KATEGORIE = [('W', 'Wiedza'), ('U', 'Umiejtnoci'), ('K', 'Kompetencje')]
    kod = models.CharField(max_length=20, unique=True)
    kategoria = models.CharField(max_length=1, choices=KATEGORIE)
    opis = models.TextField()
    def __str__(self): return self.kod

class Wykladowca(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tytul = models.CharField(max_length=50, verbose_name="Tytu/Stopie naukowy", default="dr in.")
    katedra = models.CharField(max_length=100, verbose_name="Katedra/Wydzia")
    def __str__(self): return f"{self.tytul} {self.user.first_name} {self.user.last_name}"

class EfektKierunkowy(models.Model):
    TYPY = [('W', 'Wiedza'), ('U', 'Umiejtnoci'), ('K', 'Kompetencje')]
    kod = models.CharField(max_length=20, unique=True, verbose_name="Kod efektu (np. K_W01)")
    opis = models.TextField(verbose_name="Tre efektu")
    kategoria = models.CharField(max_length=1, choices=TYPY, default='W')
    def __str__(self): return f"{self.kod} - {self.opis[:50]}..."

class KierunekStudiow(models.Model):
    POZIOMY = [('1', 'Pierwszy stopie'), ('2', 'Drugi stopie')]
    FORMY = [('S', 'Stacjonarne'), ('N', 'Niestacjonarne')]
    nazwa = models.CharField(max_length=200)
    wydzial = models.CharField(max_length=200, default="Wydzia Informatyki")
    poziom = models.CharField(max_length=1, choices=POZIOMY, default='1')
    forma = models.CharField(max_length=1, choices=FORMY, default='S')
    def __str__(self): return self.nazwa

class Modul(models.Model):
    TYPY = [('Obowizkowy', 'Obowizkowy'), ('Wybieralny', 'Wybieralny')]
    kierunek = models.ForeignKey(KierunekStudiow, on_delete=models.CASCADE)
    kod_modulu = models.CharField(max_length=50)
    nazwa = models.CharField(max_length=200)
    typ = models.CharField(max_length=20, choices=TYPY)
    semestr = models.IntegerField()
    wymagane_ects = models.IntegerField()
    def __str__(self): return f"{self.kod_modulu} ({self.typ})"

class Przedmiot(models.Model):
    STATUSY = [('ROBOCZY', 'Wersja Robocza'), ('ZATWIERDZONY', 'Zatwierdzony')]
    modul = models.ForeignKey(Modul, on_delete=models.CASCADE, related_name='przedmioty')
    status = models.CharField(max_length=20, choices=STATUSY, default='ROBOCZY')
    nazwa_pl = models.CharField(max_length=255)
    nazwa_en = models.CharField(max_length=255, blank=True)
    kod_przedmiotu = models.CharField(max_length=50)
    jezyk_wykladowy = models.CharField(max_length=50, default="Polski")
    cykl_dydaktyczny = models.CharField(max_length=20, default="2026/2027")
    badania_naukowe = models.BooleanField(default=False, verbose_name="Zwizany z badaniami?")
    ects = models.IntegerField()
    godz_wyklad = models.IntegerField(default=0)
    godz_cwiczenia = models.IntegerField(default=0)
    godz_lab = models.IntegerField(default=0)
    godz_projekt = models.IntegerField(default=0)
    godz_seminarium = models.IntegerField(default=0)
    godz_egzamin = models.IntegerField(default=0, verbose_name="Godziny na egzamin")
    efekty_kierunkowe = models.ManyToManyField(EfektKierunkowy, blank=True, verbose_name='Realizowane efekty kierunkowe')
    koordynatorzy = models.ManyToManyField(Wykladowca, related_name='przypisane_przedmioty', blank=True)
    def __str__(self): return self.nazwa_pl
    @property
    def godziny_kontaktowe(self): return (self.godz_wyklad + self.godz_cwiczenia + self.godz_lab + self.godz_projekt + self.godz_seminarium + self.godz_egzamin)
    @property
    def praca_wlasna(self):
        if hasattr(self, 'sylabus'):
            s = self.sylabus
            return ((s.pw_przygotowanie_cw or 0) + (s.pw_sprawozdania or 0) + (s.pw_projekt or 0) + (s.pw_wyklad or 0) + (s.pw_egzamin or 0) + (s.pw_literatura or 0))
        return 0

class SzczegolySylabusa(models.Model):
    przedmiot = models.OneToOneField(Przedmiot, on_delete=models.CASCADE, related_name='sylabus')
    opis_wstepny = models.TextField(verbose_name="Cele ksztacenia", blank=True, default="")
    wymagania_wstepne = models.TextField(verbose_name="Wymagania wstpne", blank=True, default="")
    efekty_wiedza = models.TextField(verbose_name="Efekty - Wiedza", default="-", blank=True)
    efekty_umiejetnosci = models.TextField(verbose_name="Efekty - Umiejtnoci", default="-", blank=True)
    efekty_kompetencje = models.TextField(verbose_name="Efekty - Kompetencje", default="-", blank=True)
    mapowanie_efektow = models.TextField(verbose_name="Relacje efektów (tekst)", blank=True, default="")
    metody_nauczania = models.TextField(verbose_name="Metody nauczania", blank=True, default="")
    formy_oceny = models.TextField(verbose_name="Metody weryfikacji wiedzy", blank=True, default="")
    zasady_oceniania = models.TextField(verbose_name="Sposoby ustalenia oceny", default="Zgodnie z regulaminem...", blank=True)
    odrabianie_zajec = models.TextField(verbose_name="Sposoby odrabiania", default="Konsultacja z prowadzcym...", blank=True)
    wymagania_obecnosci = models.TextField(verbose_name="Wymagania obecnoci", default="Obecno obowizkowa...", blank=True)
    pw_przygotowanie_cw = models.IntegerField(default=0, blank=True, null=True)
    pw_sprawozdania = models.IntegerField(default=0, blank=True, null=True)
    pw_projekt = models.IntegerField(default=0, blank=True, null=True)
    pw_wyklad = models.IntegerField(default=0, blank=True, null=True)
    pw_egzamin = models.IntegerField(default=0, blank=True, null=True)
    pw_literatura = models.IntegerField(default=0, blank=True, null=True)
    literatura = models.TextField(verbose_name="Literatura", blank=True, default="")
    badania_publikacje = models.TextField(blank=True, verbose_name="Badania i publikacje", default="")
    inne_informacje = models.TextField(blank=True, verbose_name="Inne informacje", default="")

class TrescZajec(models.Model):
    przedmiot = models.ForeignKey(Przedmiot, on_delete=models.CASCADE, related_name='harmonogram')
    numer_tematu = models.IntegerField()
    temat = models.TextField()
    liczba_godzin = models.IntegerField()

class EfektPrzedmiotowy(models.Model):
    KATEGORIE = [('W', 'Wiedza'), ('U', 'Umiejtnoci'), ('K', 'Kompetencje')]
    przedmiot = models.ForeignKey(Przedmiot, on_delete=models.CASCADE, related_name='efekty_przedmiotowe')
    kategoria = models.CharField(max_length=1, choices=KATEGORIE)
    kod_efektu_przedmiotowego = models.CharField(max_length=10, verbose_name="Kod (np. EU1)")
    opis = models.TextField()
    powiazany_efekt_kierunkowy = models.ForeignKey(EfektKierunkowy, on_delete=models.SET_NULL, null=True, blank=True)
"""

# --- PENY FORMS.PY ---
forms_ = """from django import forms
from django.contrib.auth.models import User
from .models import SzczegolySylabusa, Przedmiot, EfektKierunkowy, Wykladowca, Modul, KierunekStudiow

class PrzedmiotForm(forms.ModelForm):
    kierunek = forms.ModelChoiceField(queryset=KierunekStudiow.objects.all(), label="Kierunek Studiów")
    modul_kod = forms.CharField(label="Kod moduu")
    modul_nazwa = forms.CharField(label="Nazwa moduu")
    modul_typ = forms.ChoiceField(choices=Modul.TYPY, label="Typ Moduu")
    modul_semestr = forms.IntegerField(label="Semestr")
    modul_ects_wymagane = forms.IntegerField(label="Wymagane ECTS moduu")

    class Meta:
        model = Przedmiot
        fields = [
            'status', 'nazwa_pl', 'nazwa_en', 'kod_przedmiotu', 'jezyk_wykladowy', 
            'cykl_dydaktyczny', 'badania_naukowe', 'ects',
            'godz_wyklad', 'godz_cwiczenia', 'godz_lab', 'godz_projekt', 
            'godz_seminarium', 'godz_egzamin', 'efekty_kierunkowe', 'koordynatorzy'
        ]
        widgets = {
            'efekty_kierunkowe': forms.CheckboxSelectMultiple(),
            'koordynatorzy': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.modul:
            m = self.instance.modul
            self.fields['kierunek'].initial = m.kierunek
            self.fields['modul_kod'].initial = m.kod_modulu
            self.fields['modul_nazwa'].initial = m.nazwa
            self.fields['modul_typ'].initial = m.typ
            self.fields['modul_semestr'].initial = m.semestr
            self.fields['modul_ects_wymagane'].initial = m.wymagane_ects

        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.CheckboxInput)):
                field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})

class SylabusForm(forms.ModelForm):
    class Meta:
        model = SzczegolySylabusa
        exclude = ['przedmiot']
        widgets = {f: forms.Textarea(attrs={'class': 'form-control', 'rows': 3}) for f in ['opis_wstepny', 'wymagania_wstepne', 'literatura']}

class KierunekForm(forms.ModelForm):
    class Meta:
        model = KierunekStudiow
        fields = '__all__'

class ModulForm(forms.ModelForm):
    class Meta:
        model = Modul
        fields = '__all__'

class EfektKierunkowyForm(forms.ModelForm):
    class Meta:
        model = EfektKierunkowy
        fields = '__all__'

class WykladowcaUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    tytul = forms.CharField(max_length=50)
    katedra = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
"""

# --- PENY VIEWS.PY ---
views = """from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .models import Przedmiot, SzczegolySylabusa, TrescZajec, KierunekStudiow, Modul, Wykladowca, EfektKierunkowy
from .forms import PrzedmiotForm, WykladowcaUserForm, KierunekForm, EfektKierunkowyForm, SylabusForm

TrescZajecFormSet = inlineformset_factory(Przedmiot, TrescZajec, fields=('numer_tematu', 'temat', 'liczba_godzin'), extra=1, can_delete=True)

@login_required
def lista_przedmiotow(request):
    if request.user.is_superuser:
        return render(request, 'core/panel_zarzadzania.html', {'przedmioty': Przedmiot.objects.all(), 'kierunki': KierunekStudiow.objects.all()})
    przedmioty = Przedmiot.objects.filter(koordynatorzy__user_id=request.user.id)
    return render(request, 'core/lista.html', {'przedmioty': przedmioty})

@login_required
def zarzadzaj_przedmiotem(request, przedmiot_id=None):
    if not request.user.is_superuser: return HttpResponseForbidden()
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id) if przedmiot_id else None
    if request.method == 'POST':
        form = PrzedmiotForm(request.POST, instance=przedmiot)
        formset = TrescZajecFormSet(request.POST, instance=przedmiot)
        if form.is_valid() and formset.is_valid():
            modul, _ = Modul.objects.update_or_create(
                kod_modulu=form.cleaned_data['modul_kod'],
                defaults={
                    'kierunek': form.cleaned_data['kierunek'],
                    'nazwa': form.cleaned_data['modul_nazwa'],
                    'typ': form.cleaned_data['modul_typ'],
                    'semestr': form.cleaned_data['modul_semestr'],
                    'wymagane_ects': form.cleaned_data['modul_ects_wymagane'],
                }
            )
            p = form.save(commit=False); p.modul = modul; p.save(); form.save_m2m()
            formset.instance = p; formset.save()
            return redirect('lista_przedmiotow')
    else:
        form = PrzedmiotForm(instance=przedmiot)
        formset = TrescZajecFormSet(instance=przedmiot)
    return render(request, 'core/formularz_przedmiotu.html', {'form': form, 'formset': formset, 'przedmiot': przedmiot})

@login_required
def dodaj_wykladowce(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = WykladowcaUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save(commit=False); u.set_password(form.cleaned_data['password']); u.save()
        Wykladowca.objects.create(user=u, tytul=form.cleaned_data['tytul'], katedra=form.cleaned_data['katedra'])
        return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Nowy Wykadowca'})

@login_required
def dodaj_kierunek(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = KierunekForm(request.POST or None)
    if form.is_valid(): form.save(); return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Nowy Kierunek'})

@login_required
def dodaj_efekt(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = EfektKierunkowyForm(request.POST or None)
    if form.is_valid(): form.save(); return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Nowy Efekt'})
"""

# --- PENY HTML ---
html = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8fafc; }
        .section-header { background: #1e293b; color: white; padding: 10px; border-radius: 8px; margin: 25px 0 10px 0; font-weight: bold; }
        .card { border: none; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        .multi-select { background: white; border: 1px solid #cbd5e1; padding: 10px; max-height: 200px; overflow-y: auto; border-radius: 8px; }
    </style>
</head>
<body>
<div class="container py-5">
    <form method="post" class="card p-4 shadow">
        {% csrf_token %}
        <h2 class="text-primary fw-bold mb-4">Kombajn Prodziekana: Przedmiot + Modu</h2>
        
        <div class="section-header">1. Dane Moduu</div>
        <div class="row g-3">
            <div class="col-md-6"><label class="fw-bold">Kierunek</label>{{ form.kierunek }}</div>
            <div class="col-md-3"><label class="fw-bold">Kod Moduu</label>{{ form.modul_kod }}</div>
            <div class="col-md-3"><label class="fw-bold">Typ</label>{{ form.modul_typ }}</div>
            <div class="col-md-6"><label class="fw-bold">Nazwa Moduu</label>{{ form.modul_nazwa }}</div>
            <div class="col-md-3"><label class="fw-bold">Semestr</label>{{ form.modul_semestr }}</div>
            <div class="col-md-3"><label class="fw-bold">Wymagane ECTS moduu</label>{{ form.modul_ects_wymagane }}</div>
        </div>

        <div class="section-header">2. Dane Przedmiotu</div>
        <div class="row g-3">
            <div class="col-md-3"><label class="fw-bold">Status</label>{{ form.status }}</div>
            <div class="col-md-9"><label class="fw-bold">Nazwa PL</label>{{ form.nazwa_pl }}</div>
            <div class="col-md-6"><label class="fw-bold">Nazwa EN</label>{{ form.nazwa_en }}</div>
            <div class="col-md-3"><label class="fw-bold">Kod Przedmiotu</label>{{ form.kod_przedmiotu }}</div>
            <div class="col-md-3"><label class="fw-bold">ECTS</label>{{ form.ects }}</div>
        </div>

        <div class="section-header">3. Godziny</div>
        <div class="row row-cols-6 g-2 text-center">
            <div class="col"><label class="small fw-bold">Wykad</label>{{ form.godz_wyklad }}</div>
            <div class="col"><label class="small fw-bold">wicz.</label>{{ form.godz_cwiczenia }}</div>
            <div class="col"><label class="small fw-bold">Lab.</label>{{ form.godz_lab }}</div>
            <div class="col"><label class="small fw-bold">Proj.</label>{{ form.godz_projekt }}</div>
            <div class="col"><label class="small fw-bold">Sem.</label>{{ form.godz_seminarium }}</div>
            <div class="col"><label class="small fw-bold">Egz.</label>{{ form.godz_egzamin }}</div>
        </div>

        <div class="section-header">4. Harmonogram</div>
        {{ formset.management_form }}
        <table class="table table-bordered bg-white">
            <thead class="table-dark"><tr><th>Nr</th><th>Temat</th><th>Godz</th><th>Usu</th></tr></thead>
            <tbody>
                {% for f in formset %}
                <tr>
                    <td>{{ f.numer_tematu }}</td><td>{{ f.temat }}</td><td>{{ f.liczba_godzin }}</td><td>{{ f.DELETE }}</td>
                    {% for h in f.hidden_fields %}{{ h }}{% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="section-header">5. Relacje</div>
        <div class="row g-3">
            <div class="col-md-6"><label class="fw-bold mb-2">Efekty Kierunkowe</label><div class="multi-select">{{ form.efekty_kierunkowe }}</div></div>
            <div class="col-md-6"><label class="fw-bold mb-2">Koordynatorzy</label><div class="multi-select">{{ form.koordynatorzy }}</div></div>
        </div>

        <div class="mt-5 d-flex justify-content-between border-top pt-4">
            <a href="/" class="btn btn-outline-secondary px-4">Anuluj</a>
            <button type="submit" class="btn btn-primary px-5 shadow">Zapisz Wszystko</button>
        </div>
    </form>
</div>
</body>
</html>"""

zapisz("core/models.py", models)
zapisz("core/forms.py", forms_)
zapisz("core/views.py", views)
zapisz("core/templates/core/formularz_przedmiotu.html", html)
