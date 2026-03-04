from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Wykladowca, KierunekStudiow, Modul, EfektKierunkowy, Przedmiot, SzczegolySylabusa, TrescZajec


class Command(BaseCommand):
    help = 'Wgrywa potężną, rozbudowaną bazę danych dla Wydziału Informatyki (z bogatą matrycą efektów).'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Sprzątam starą bazę danych...")

        TrescZajec.objects.all().delete()
        SzczegolySylabusa.objects.all().delete()
        Przedmiot.objects.all().delete()
        Modul.objects.all().delete()
        KierunekStudiow.objects.all().delete()
        EfektKierunkowy.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("✅ Baza czysta. Twoje konto 'admin' ocalało!"))

        self.stdout.write("👨‍🏫 Generuję konta wykładowców...")
        users_data = [
            ('jkowalski', 'Jan', 'Kowalski', 'dr inż.', 'Katedra Inżynierii Oprogramowania'),
            ('anowak', 'Anna', 'Nowak', 'dr', 'Katedra Sztucznej Inteligencji'),
            ('pwisniewski', 'Piotr', 'Wiśniewski', 'prof. dr hab.', 'Katedra Systemów Złożonych'),
            ('mwojcik', 'Maria', 'Wójcik', 'mgr inż.', 'Katedra Sieci Komputerowych'),
            ('tkaczmarek', 'Tomasz', 'Kaczmarek', 'dr inż.', 'Katedra Algorytmiki')
        ]
        wykladowcy = {}
        for username, imie, nazwisko, tytul, katedra in users_data:
            u = User.objects.create_user(username=username, password='123', first_name=imie, last_name=nazwisko)
            wykladowcy[username] = Wykladowca.objects.create(user=u, tytul=tytul, katedra=katedra)

        self.stdout.write("🎓 Tworzę kierunki studiów i moduły...")
        k_inf = KierunekStudiow.objects.create(nazwa='Informatyka', wydzial='Wydział Informatyki', poziom='1',
                                               forma='S', koordynator=wykladowcy['jkowalski'])
        k_si = KierunekStudiow.objects.create(nazwa='Sztuczna Inteligencja', wydzial='Wydział Informatyki', poziom='2',
                                              forma='S', koordynator=wykladowcy['anowak'])

        m_inf_1 = Modul.objects.create(kierunek=k_inf, kod_modulu='INF-1-OBO', nazwa='Obowiązkowe Semestr 1',
                                       typ='Obowiązkowy', semestr=1, wymagane_ects=30)
        m_inf_2 = Modul.objects.create(kierunek=k_inf, kod_modulu='INF-2-OBO', nazwa='Obowiązkowe Semestr 2',
                                       typ='Obowiązkowy', semestr=2, wymagane_ects=30)
        m_si_1 = Modul.objects.create(kierunek=k_si, kod_modulu='SI-1-OBO', nazwa='Rdzeń Sztucznej Inteligencji',
                                      typ='Obowiązkowy', semestr=1, wymagane_ects=30)

        self.stdout.write("🧠 Buduję POTĘŻNĄ matrycę efektów uczenia się...")

        # Słownik, w którym przechowamy wszystkie wygenerowane efekty
        efekty = {}

        # --- WIEDZA (W) ---
        efekty['K_W01'] = EfektKierunkowy.objects.create(kod='K_W01', kategoria='W',
                                                         opis='Zna matematyczne podstawy informatyki, w tym logikę i matematykę dyskretną.')
        efekty['K_W02'] = EfektKierunkowy.objects.create(kod='K_W02', kategoria='W',
                                                         opis='Zna zasady projektowania i inżynierii oprogramowania oraz cykl życia systemów.')
        efekty['K_W03'] = EfektKierunkowy.objects.create(kod='K_W03', kategoria='W',
                                                         opis='Ma uporządkowaną wiedzę w zakresie architektury systemów komputerowych i sieci.')
        efekty['K_W04'] = EfektKierunkowy.objects.create(kod='K_W04', kategoria='W',
                                                         opis='Rozumie podstawowe zagadnienia cyberbezpieczeństwa i ochrony danych.')
        efekty['K_W05'] = EfektKierunkowy.objects.create(kod='K_W05', kategoria='W',
                                                         opis='Zna podstawowe algorytmy i struktury danych oraz metody oceny ich złożoności.')
        efekty['SI_W01'] = EfektKierunkowy.objects.create(kod='SI_W01', kategoria='W',
                                                          opis='Ma pogłębioną wiedzę z zakresu uczenia maszynowego i sieci neuronowych.')
        efekty['SI_W02'] = EfektKierunkowy.objects.create(kod='SI_W02', kategoria='W',
                                                          opis='Zna zaawansowane metody przetwarzania języka naturalnego (NLP).')

        # --- UMIEJĘTNOŚCI (U) ---
        efekty['K_U01'] = EfektKierunkowy.objects.create(kod='K_U01', kategoria='U',
                                                         opis='Potrafi napisać poprawny, zoptymalizowany kod w co najmniej jednym języku obiektowym.')
        efekty['K_U02'] = EfektKierunkowy.objects.create(kod='K_U02', kategoria='U',
                                                         opis='Potrafi projektować i administrować relacyjnymi bazami danych (SQL).')
        efekty['K_U03'] = EfektKierunkowy.objects.create(kod='K_U03', kategoria='U',
                                                         opis='Umie testować oprogramowanie z wykorzystaniem testów jednostkowych i integracyjnych.')
        efekty['K_U04'] = EfektKierunkowy.objects.create(kod='K_U04', kategoria='U',
                                                         opis='Potrafi pracować z systemami kontroli wersji (np. Git).')
        efekty['K_U05'] = EfektKierunkowy.objects.create(kod='K_U05', kategoria='U',
                                                         opis='Posiada umiejętność tworzenia responsywnych aplikacji webowych.')
        efekty['SI_U01'] = EfektKierunkowy.objects.create(kod='SI_U01', kategoria='U',
                                                          opis='Potrafi trenować i optymalizować głębokie sieci neuronowe z użyciem PyTorch/TensorFlow.')

        # --- KOMPETENCJE (K) ---
        efekty['K_K01'] = EfektKierunkowy.objects.create(kod='K_K01', kategoria='K',
                                                         opis='Rozumie potrzebę ciągłego dokształcania się i podnoszenia kompetencji zawodowych.')
        efekty['K_K02'] = EfektKierunkowy.objects.create(kod='K_K02', kategoria='K',
                                                         opis='Potrafi efektywnie pracować i współdziałać w zespole programistycznym (np. Scrum).')
        efekty['K_K03'] = EfektKierunkowy.objects.create(kod='K_K03', kategoria='K',
                                                         opis='Potrafi odpowiednio określić priorytety służące realizacji ustalonego zadania.')
        efekty['SI_K01'] = EfektKierunkowy.objects.create(kod='SI_K01', kategoria='K',
                                                          opis='Zna i stosuje zasady etyki w rozwoju algorytmów sztucznej inteligencji.')

        self.stdout.write("📚 Rejestruję przedmioty i ich sylabusy...")

        # Przedmiot 1: ZATWIERDZONY
        p1 = Przedmiot.objects.create(modul=m_inf_1, status='ZATWIERDZONY', nazwa_pl='Wstęp do programowania',
                                      nazwa_en='Introduction to Programming', kod_przedmiotu='INF-WDP', ects=6,
                                      godz_wyklad=30, godz_lab=30)
        p1.efekty_kierunkowe.add(efekty['K_W05'], efekty['K_U01'], efekty['K_K01'])
        p1.koordynatorzy.add(wykladowcy['tkaczmarek'])
        SzczegolySylabusa.objects.create(przedmiot=p1,
                                         opis_wstepny='W | O1 | Zrozumienie pętli i instrukcji warunkowych\n---METODY---\nW | Kolokwium')

        # Przedmiot 2: WERYFIKACJA (Czeka na Szefa Informatyki)
        p2 = Przedmiot.objects.create(modul=m_inf_2, status='WERYFIKACJA', nazwa_pl='Bazy Danych SQL',
                                      nazwa_en='SQL Databases', kod_przedmiotu='INF-BD', ects=5, godz_wyklad=15,
                                      godz_lab=30)
        p2.efekty_kierunkowe.add(efekty['K_W01'], efekty['K_U02'], efekty['K_K02'])
        p2.koordynatorzy.add(wykladowcy['pwisniewski'])
        SzczegolySylabusa.objects.create(przedmiot=p2,
                                         opis_wstepny='W | O1 | Algebra relacji\nU | O2 | Pisanie złączeń JOIN\n---METODY---\nW | Egzamin\nU | Projekt')
        TrescZajec.objects.create(przedmiot=p2, numer_tematu=1,
                                  temat='[wykład|K_W01] Architektura systemów bazodanowych', liczba_godzin=2)
        TrescZajec.objects.create(przedmiot=p2, numer_tematu=2, temat='[laboratorium|K_U02] Projektowanie schematów',
                                  liczba_godzin=2)

        # Przedmiot 3: SPRAWDZONY (Czeka na Prodziekana)
        p3 = Przedmiot.objects.create(modul=m_inf_2, status='SPRAWDZONY', nazwa_pl='Inżynieria Oprogramowania',
                                      nazwa_en='Software Engineering', kod_przedmiotu='INF-IO', ects=6, godz_wyklad=30,
                                      godz_projekt=30)
        p3.efekty_kierunkowe.add(efekty['K_W02'], efekty['K_U03'], efekty['K_U04'], efekty['K_K02'])
        p3.koordynatorzy.add(wykladowcy['jkowalski'])
        SzczegolySylabusa.objects.create(przedmiot=p3,
                                         opis_wstepny='W | O1 | Metodyki Zwinne Scrum\n---METODY---\nW | Egzamin')

        # Przedmiot 4: DO_POPRAWY
        p4 = Przedmiot.objects.create(modul=m_inf_2, status='DO_POPRAWY',
                                      uwagi_statusu="Proszę dodać więcej godzin do pracy własnej studenta, obecnie ECTS się nie zgadzają z bilansem godzinowym.",
                                      nazwa_pl='Aplikacje Webowe', nazwa_en='Web Applications',
                                      kod_przedmiotu='INF-WEB', ects=4, godz_wyklad=15, godz_lab=30)
        p4.efekty_kierunkowe.add(efekty['K_W04'], efekty['K_U05'])
        p4.koordynatorzy.add(wykladowcy['mwojcik'])
        SzczegolySylabusa.objects.create(przedmiot=p4, pw_wyklad=0)

        # Przedmiot 5: ROBOCZY
        p5 = Przedmiot.objects.create(modul=m_si_1, status='ROBOCZY', nazwa_pl='Uczenie Maszynowe',
                                      nazwa_en='Machine Learning', kod_przedmiotu='SI-ML', ects=8, godz_wyklad=30,
                                      godz_lab=45)
        p5.efekty_kierunkowe.add(efekty['SI_W01'], efekty['SI_U01'], efekty['SI_K01'])
        p5.koordynatorzy.add(wykladowcy['anowak'], wykladowcy['tkaczmarek'])
        SzczegolySylabusa.objects.create(przedmiot=p5,
                                         opis_wstepny='W | O1 | Regresja Liniowa\n---METODY---\nW | Kolokwium')

        self.stdout.write(self.style.SUCCESS("🚀 Gotowe! Uczelnia załadowana poprawnie."))