from django.db import models
from django.contrib.auth.models import User

# --- SOWNIKI ---
class EfektUczenia(models.Model):
    KATEGORIE = [('W', 'Wiedza'), ('U', 'Umiejtnoci'), ('K', 'Kompetencje')]
    kod = models.CharField(max_length=20, unique=True)
    kategoria = models.CharField(max_length=1, choices=KATEGORIE)
    opis = models.TextField()
    def __str__(self): return self.kod

# NOWO: Sownik Efektów Kierunkowych (z Excela)
class EfektKierunkowy(models.Model):
    TYPY = [('W', 'Wiedza'), ('U', 'Umiejtnoci'), ('K', 'Kompetencje')]
    kod = models.CharField(max_length=20, unique=True, verbose_name="Kod efektu (np. K_W01)")
    opis = models.TextField(verbose_name="Tre efektu")
    kategoria = models.CharField(max_length=1, choices=TYPY, default='W')
    
    def __str__(self):
        return f"{self.kod} - {self.opis[:50]}..."

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
    opiekun = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='przedmioty')
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

    # RELACJE
    efekty = models.ManyToManyField(EfektUczenia, blank=True, related_name='przedmioty')
    
    # NOWO: Checkboxy do efektów kierunkowych
    efekty_kierunkowe = models.ManyToManyField(EfektKierunkowy, blank=True, verbose_name="Realizowane efekty kierunkowe")

    def __str__(self): return self.nazwa_pl

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

    def __str__(self): return f"Sylabus: {self.przedmiot.nazwa_pl}"

class TrescZajec(models.Model):
    przedmiot = models.ForeignKey(Przedmiot, on_delete=models.CASCADE, related_name='harmonogram')
    numer_tematu = models.IntegerField()
    temat = models.TextField()
    liczba_godzin = models.IntegerField()
