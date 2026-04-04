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
        ('WERYFIKACJA', 'Do sprawdzenia (Koordynator Kierunku)'),
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