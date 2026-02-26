from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from .models import Przedmiot, SzczegolySylabusa, TrescZajec, KierunekStudiow, Modul, EfektKierunkowy, Wykladowca
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
                semestry_data.append({
                    'numer': s, 'suma': suma, 'liczba': liczba, 'alert': suma != 30
                })
        if semestry_data:
            statystyki_ects.append({'nazwa': k.nazwa, 'semestry': semestry_data})

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
        form = PrzedmiotForm(request.POST, instance=przedmiot)
        if form.is_valid():
            p = form.save(commit=False)
            k, s, t = form.cleaned_data['kierunek'], form.cleaned_data['semestr'], form.cleaned_data['typ_zajec']
            modul, _ = Modul.objects.get_or_create(
                kierunek=k, semestr=s, typ=t,
                defaults={'kod_modulu': f"{k.nazwa[:3].upper()}-{s}-{t[:3].upper()}", 'nazwa': f"{t} - Semestr {s}",
                          'wymagane_ects': 30}
            )
            p.modul = modul
            p.save()
            form.save_m2m()  # Zapisujemy podstawowe M2M (np. koordynatorów)

            # --- NAPRAWA ZAPISU EFEKTÓW ---
            # 1. Usuwamy te, które Prodziekan zaznaczył do kosza
            usun_ids = request.POST.getlist('usun_efekt')
            if usun_ids:
                p.efekty_kierunkowe.filter(id__in=usun_ids).delete()

            # 2. Dodajemy zupełnie nowe efekty z pól tekstowych
            katy = request.POST.getlist('nowy_efekt_kat')
            opisy = request.POST.getlist('nowy_efekt_opis')

            for kt, op in zip(katy, opisy):
                if op.strip():
                    # Liczymy ile jest efektów w tej kategorii, żeby nadać numer (np. K_W03)
                    istniejace = EfektKierunkowy.objects.filter(kategoria=kt)
                    max_num = 0
                    for e in istniejace:
                        match = re.search(r'(\d+)$', e.kod)
                        if match: max_num = max(max_num, int(match.group(1)))

                    nowy_kod = f"K_{kt}{max_num + 1:02d}"
                    ne = EfektKierunkowy.objects.create(kod=nowy_kod, kategoria=kt, opis=op.strip())
                    p.efekty_kierunkowe.add(ne)  # DODAJEMY DO PRZEDMIOTU

            p.save()  # Finałowy zapis
            return redirect('lista_przedmiotow')
    else:
        initial_data = {}
        if przedmiot and przedmiot.modul:
            initial_data = {'kierunek': przedmiot.modul.kierunek, 'semestr': przedmiot.modul.semestr,
                            'typ_zajec': przedmiot.modul.typ}
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
        form = SylabusForm(request.POST, instance=sylabus)
        if form.is_valid():
            form.save()
            wybrane = form.cleaned_data.get('efekty_kierunkowe')
            if wybrane is not None:
                przedmiot.efekty_kierunkowe.set(wybrane)

            # Harmonogram Smart Paste
            raw = form.cleaned_data.get('harmonogram_raw')
            if raw:
                TrescZajec.objects.filter(przedmiot=przedmiot).delete()
                for i, line in enumerate(raw.strip().split('\n'), 1):
                    if line.strip():
                        TrescZajec.objects.create(przedmiot=przedmiot, numer_tematu=i, temat=line.strip(),
                                                  liczba_godzin=2)
            return redirect('edycja_sylabusa', przedmiot_id=przedmiot.id)
    else:
        harmonogram_text = "\n".join(
            [t.temat for t in TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')])
        form = SylabusForm(instance=sylabus, initial={
            "efekty_kierunkowe": przedmiot.efekty_kierunkowe.all(),
            "harmonogram_raw": harmonogram_text
        })
        # WAŻNE: Ograniczamy listę efektów tylko do tych, które Prodziekan przypisał do tego przedmiotu
        form.fields["efekty_kierunkowe"].queryset = przedmiot.efekty_kierunkowe.all()

    # Logika dekodowania tematów do widoku (wykłady/ćwiczenia)
    tematy_db = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    tematy_zdekodowane = []
    counters = {}
    for t in tematy_db:
        tresc, forma, efekty = t.temat, 'wykład', ''
        if tresc.startswith('['):
            end_idx = tresc.find(']')
            if end_idx != -1:
                meta, tresc = tresc[1:end_idx], tresc[end_idx + 1:].strip()
                parts = meta.split('|');
                forma = parts[0].strip()
                if len(parts) > 1: efekty = parts[1].strip()
        counters[forma] = counters.get(forma, 0) + 1
        tematy_zdekodowane.append({'lp': counters[forma], 'tresc': tresc, 'efekty': efekty, 'forma': forma})

    return render(request, 'core/edycja_sylabusa.html',
                  {'form': form, 'przedmiot': przedmiot, 'tematy': tematy_zdekodowane})


@login_required
def grid_kierunku(request, kierunek_id):
    kierunek = get_object_or_404(KierunekStudiow, id=kierunek_id)
    return HttpResponse(f"Grid dla {kierunek.nazwa} (W budowie)")


@login_required
def pobierz_pdf(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    sylabus, _ = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)

    # 1. PRZYGOTOWANIE HARMONOGRAMU (TEMATY)
    tematy_db = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    tematy_zdekodowane = []
    counters = {}
    for t in tematy_db:
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

    # 2. ROZKODOWANIE CELÓW I METOD Z POLA UKRYTEGO
    cele_lista = []
    metody_dict = {'W': '-', 'U': '-', 'K': '-'}
    if sylabus.opis_wstepny:
        mode = 'cele'
        for line in sylabus.opis_wstepny.split('\n'):
            line = line.strip()
            if not line: continue
            if line == '---METODY---':
                mode = 'metody'
                continue
            parts = [p.strip() for p in line.split('|')]
            if mode == 'cele' and len(parts) >= 3:
                cele_lista.append({'kategoria': parts[0], 'kod': parts[1], 'tresc': parts[2]})
            elif mode == 'metody' and len(parts) >= 2:
                metody_dict[parts[0]] = parts[1]

    # 3. PRZYGOTOWANIE MATRYCY EFEKTÓW (Z PODZIAŁEM NA W, U, K)
    efekty_W, efekty_U, efekty_K = [], [], []
    licznik_W, licznik_U, licznik_K = 1, 1, 1

    for e in przedmiot.efekty_kierunkowe.all().order_by('kategoria', 'kod'):
        # Szukamy, które cele pasują do tej kategorii
        cele_dla_kategorii = [c['kod'] for c in cele_lista if c['kategoria'] == e.kategoria]
        cele_str = ", ".join(cele_dla_kategorii) if cele_dla_kategorii else "-"
        metoda = metody_dict.get(e.kategoria, "-")

        if e.kategoria == 'W':
            efekty_W.append(
                {'symbol': f"EU_W{licznik_W:02d}", 'opis': e.opis, 'kod': e.kod, 'cele': cele_str, 'metoda': metoda})
            licznik_W += 1
        elif e.kategoria == 'U':
            efekty_U.append(
                {'symbol': f"EU_U{licznik_U:02d}", 'opis': e.opis, 'kod': e.kod, 'cele': cele_str, 'metoda': metoda})
            licznik_U += 1
        elif e.kategoria == 'K':
            efekty_K.append(
                {'symbol': f"EU_K{licznik_K:02d}", 'opis': e.opis, 'kod': e.kod, 'cele': cele_str, 'metoda': metoda})
            licznik_K += 1

    # 4. OBLICZENIA MATEMATYCZNE GODZIN (DLA TABELI OBCIĄŻEŃ)
    p_cw = sylabus.pw_przygotowanie_cw or 0
    p_lab = sylabus.pw_sprawozdania or 0
    p_proj = sylabus.pw_projekt or 0
    p_wyk = sylabus.pw_wyklad or 0
    p_egz = sylabus.pw_egzamin or 0
    p_lit = sylabus.pw_literatura or 0

    h_egz = 2 if p_egz > 0 else 0
    sum_kon = przedmiot.godz_wyklad + przedmiot.godz_cwiczenia + przedmiot.godz_lab + przedmiot.godz_projekt + przedmiot.godz_seminarium + h_egz
    sum_wla = p_cw + p_lab + p_proj + p_wyk + p_egz + p_lit
    sum_tot = sum_kon + sum_wla

    # 5. WYSYŁKA WSZYSTKIEGO DO SZABLONU PDF
    html_string = render_to_string('core/sylabus_pdf.html', {
        'przedmiot': przedmiot,
        'sylabus': sylabus,
        'tematy': tematy_zdekodowane,
        'cele_lista': cele_lista,
        'efekty_W': efekty_W,
        'efekty_U': efekty_U,
        'efekty_K': efekty_K,
        'p_cw': p_cw, 'p_lab': p_lab, 'p_proj': p_proj, 'p_wyk': p_wyk, 'p_egz': p_egz, 'p_lit': p_lit,
        'h_egz': h_egz,
        'sum_kon': sum_kon,
        'sum_wla': sum_wla,
        'sum_tot': sum_tot
    })

    return HttpResponse(HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(),
                        content_type='application/pdf')


@login_required
def dodaj_wykladowce(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = WykladowcaUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save(commit=False);
        u.set_password(form.cleaned_data['password']);
        u.save()
        Wykladowca.objects.create(user=u, tytul=form.cleaned_data['tytul'], katedra=form.cleaned_data['katedra'])
        return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Dodaj Wykładowcę'})


@login_required
def dodaj_kierunek(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = KierunekForm(request.POST or None)
    if form.is_valid(): form.save(); return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Dodaj Kierunek'})