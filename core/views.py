from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from .models import Przedmiot, SzczegolySylabusa, TrescZajec, KierunekStudiow, Modul, EfektKierunkowy, Wykladowca, \
    Komentarz
from .forms import SylabusForm, PrzedmiotForm, WykladowcaUserForm, KierunekForm
from django.db.models import Sum
import re


@login_required
def lista_przedmiotow(request):
    wykladowca = getattr(request.user, 'wykladowca', None)
    is_admin = request.user.is_superuser

    wszystkie_lata = Przedmiot.objects.values_list('cykl_dydaktyczny', flat=True).distinct().order_by(
        '-cykl_dydaktyczny')
    wybrany_rok = request.GET.get('rok')
    if not wybrany_rok and wszystkie_lata:
        wybrany_rok = wszystkie_lata[0]

    wszystkie_kierunki = KierunekStudiow.objects.all()  # <--- DODANO DO WYBORU W OKIENKU KLONOWANIA

    if is_admin:
        kierunki_pod_opieka = wszystkie_kierunki
        przedmioty_kierunku = Przedmiot.objects.filter(cykl_dydaktyczny=wybrany_rok)
        moje_prowadzone = Przedmiot.objects.filter(koordynatorzy__user=request.user, cykl_dydaktyczny=wybrany_rok)
        tryb_nazwa = "Panel Prodziekana"
    elif wykladowca:
        kierunki_pod_opieka = KierunekStudiow.objects.filter(koordynator=wykladowca)
        przedmioty_kierunku = Przedmiot.objects.filter(modul__kierunek__in=kierunki_pod_opieka,
                                                       cykl_dydaktyczny=wybrany_rok)
        moje_prowadzone = Przedmiot.objects.filter(koordynatorzy=wykladowca, cykl_dydaktyczny=wybrany_rok)
        tryb_nazwa = "Panel Wykładowcy / Koordynatora"
    else:
        return HttpResponse("Błąd: Brak uprawnień profilowych.")

    wszystkie_widoczne = (przedmioty_kierunku | moje_prowadzone).distinct()

    statystyki_ects = []
    for k in kierunki_pod_opieka:
        semestry_data = []
        for s in range(1, 9):
            przedmioty_sem = Przedmiot.objects.filter(modul__kierunek=k, modul__semestr=s, cykl_dydaktyczny=wybrany_rok)
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
        'is_dean': is_admin,
        'wszystkie_lata': wszystkie_lata,
        'wybrany_rok': wybrany_rok,
        'wszystkie_kierunki': wszystkie_kierunki  # <--- PRZEKAZANIE DO SZABLONU
    })


@login_required
def zarzadzaj_przedmiotem(request, przedmiot_id=None):
    is_dean = request.user.is_superuser
    wykladowca = getattr(request.user, 'wykladowca', None)
    wszystkie_kierunki = KierunekStudiow.objects.all()  # <--- DODANO DO WYBORU W OKIENKU KLONOWANIA

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
                defaults={'kod_modulu': f"{k.nazwa[:3].upper()}-{s}-{t[:3].upper()}", 'nazwa': f"{t} - Semestr {s}",
                          'wymagane_ects': 30}
            )
            p.modul = modul
            p.save()
            form.save_m2m()

            usun_ids = request.POST.getlist('usun_efekt')
            if usun_ids: p.efekty_kierunkowe.remove(*usun_ids)

            for kt, op in zip(request.POST.getlist('nowy_efekt_kat'), request.POST.getlist('nowy_efekt_opis')):
                if op.strip():
                    istniejace = EfektKierunkowy.objects.filter(kategoria=kt)
                    max_num = 0
                    for e in istniejace:
                        match = re.search(r'(\d+)$', e.kod)
                        if match: max_num = max(max_num, int(match.group(1)))
                    p.efekty_kierunkowe.add(
                        EfektKierunkowy.objects.create(kod=f"K_{kt}{max_num + 1:02d}", kategoria=kt, opis=op.strip()))

            p.save()
            return redirect('lista_przedmiotow')
    else:
        initial_data = {'kierunek': przedmiot.modul.kierunek, 'semestr': przedmiot.modul.semestr,
                        'typ_zajec': przedmiot.modul.typ} if przedmiot and hasattr(przedmiot, 'modul') else {}
        form = PrzedmiotForm(instance=przedmiot, initial=initial_data)

    return render(request, 'core/formularz_przedmiotu.html', {
        'form': form, 'przedmiot': przedmiot, 'is_dean': is_dean, 'wszystkie_kierunki': wszystkie_kierunki
    })


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
                for i, line in enumerate(raw.strip().split('\n'), 1):
                    if line.strip(): TrescZajec.objects.create(przedmiot=przedmiot, numer_tematu=i, temat=line.strip(),
                                                               liczba_godzin=2)

            if 'przekaz_dalej' in request.POST:
                przedmiot.status = 'WERYFIKACJA'
                przedmiot.save()
                return redirect('lista_przedmiotow')

            return redirect('edycja_sylabusa', przedmiot_id=przedmiot.id)
    else:
        form = SylabusForm(instance=sylabus, initial={
            "efekty_kierunkowe": przedmiot.efekty_kierunkowe.all(),
            "harmonogram_raw": "\n".join(
                [t.temat for t in TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')])
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

    return render(request, 'core/edycja_sylabusa.html',
                  {'form': form, 'przedmiot': przedmiot, 'tematy': tematy_zdekodowane})


# --- ZMODYFIKOWANA LOGIKA KLONOWANIA ---
def wykonaj_klonowanie(stary_p, nowy_rok=None, nowy_kierunek_id=None):
    if not nowy_rok:
        try:
            lata = stary_p.cykl_dydaktyczny.split('/')
            nowy_rok = f"{int(lata[0]) + 1}/{int(lata[1]) + 1}"
        except:
            nowy_rok = stary_p.cykl_dydaktyczny + " (Kopia)"

    # Znajdź lub stwórz odpowiedni moduł dla wybranego (nowego lub tego samego) kierunku
    nowy_modul = stary_p.modul
    if nowy_kierunek_id and str(nowy_modul.kierunek.id) != str(nowy_kierunek_id):
        nowy_kierunek = KierunekStudiow.objects.get(id=nowy_kierunek_id)
        nowy_modul, _ = Modul.objects.get_or_create(
            kierunek=nowy_kierunek,
            semestr=stary_p.modul.semestr,
            typ=stary_p.modul.typ,
            defaults={
                'kod_modulu': f"{nowy_kierunek.nazwa[:3].upper()}-{stary_p.modul.semestr}-{stary_p.modul.typ[:3].upper()}",
                'nazwa': f"{stary_p.modul.typ} - Semestr {stary_p.modul.semestr}",
                'wymagane_ects': 30
            }
        )

    stare_efekty = list(stary_p.efekty_kierunkowe.all())
    stali_koordynatorzy = list(stary_p.koordynatorzy.all())
    stary_harmonogram = list(stary_p.harmonogram.all())
    try:
        stary_sylabus = stary_p.sylabus
    except SzczegolySylabusa.DoesNotExist:
        stary_sylabus = None

    stary_p.pk = None
    stary_p.status = 'ROBOCZY'
    stary_p.cykl_dydaktyczny = nowy_rok
    stary_p.modul = nowy_modul
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

    if request.method == 'POST':
        nowy_rok = request.POST.get('nowy_rok')
        obecny_rok = request.POST.get('obecny_rok')

        # Klonujemy TYLKO przedmioty z roku, który Prodziekan miał aktualnie wybrany w filtrze
        if obecny_rok:
            przedmioty = Przedmiot.objects.filter(modul__kierunek_id=kierunek_id, cykl_dydaktyczny=obecny_rok)
        else:
            przedmioty = Przedmiot.objects.filter(modul__kierunek_id=kierunek_id)

        for p in przedmioty:
            wykonaj_klonowanie(p, nowy_rok=nowy_rok)

    return redirect('lista_przedmiotow')


@login_required
def klonuj_przedmiot_widok(request, przedmiot_id):
    if not request.user.is_superuser: return HttpResponseForbidden()
    p = get_object_or_404(Przedmiot, id=przedmiot_id)

    if request.method == 'POST':
        nowy_rok = request.POST.get('nowy_rok')
        kierunek_id = request.POST.get('kierunek_id')
        wykonaj_klonowanie(p, nowy_rok, kierunek_id)
    else:
        wykonaj_klonowanie(p)

    return redirect('lista_przedmiotow')


@login_required
def grid_kierunku(request, kierunek_id):
    kierunek = get_object_or_404(KierunekStudiow, id=kierunek_id)
    return HttpResponse(f"Grid dla {kierunek.nazwa} (W budowie)")


@login_required
def pobierz_pdf(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    sylabus, _ = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)

    p_cw = sylabus.pw_przygotowanie_cw or 0
    p_lab = sylabus.pw_sprawozdania or 0
    p_proj = sylabus.pw_projekt or 0
    p_wyk = sylabus.pw_wyklad or 0
    p_egz = sylabus.pw_egzamin or 0
    p_lit = sylabus.pw_literatura or 0
    sum_wla = p_cw + p_lab + p_proj + p_wyk + p_egz + p_lit

    h_egz = 2 if p_egz > 0 else 0
    sum_kon = (przedmiot.godz_wyklad + przedmiot.godz_cwiczenia +
               przedmiot.godz_lab + przedmiot.godz_projekt +
               przedmiot.godz_seminarium + h_egz)
    sum_tot = sum_kon + sum_wla

    cele_lista = []
    metody = {'W': '-', 'U': '-', 'K': '-'}
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
                cele_lista.append({'kat': parts[0], 'kod': parts[1], 'tresc': parts[2]})
            elif mode == 'metody' and len(parts) >= 2:
                metody[parts[0]] = parts[1]

    efekty_W, efekty_U, efekty_K = [], [], []
    kierunkowe = przedmiot.efekty_kierunkowe.all().order_by('kategoria', 'kod')

    cele_W = ", ".join([c['kod'] for c in cele_lista if c['kat'] == 'W'])
    cele_U = ", ".join([c['kod'] for c in cele_lista if c['kat'] == 'U'])
    cele_K = ", ".join([c['kod'] for c in cele_lista if c['kat'] == 'K'])

    c_w, c_u, c_k = 1, 1, 1
    for e in kierunkowe:
        if e.kategoria == 'W':
            efekty_W.append({'symbol': f'EU_W{c_w:02d}', 'opis': e.opis, 'kod': e.kod, 'cele': cele_W,
                             'metoda': metody.get('W', '-')})
            c_w += 1
        elif e.kategoria == 'U':
            efekty_U.append({'symbol': f'EU_U{c_u:02d}', 'opis': e.opis, 'kod': e.kod, 'cele': cele_U,
                             'metoda': metody.get('U', '-')})
            c_u += 1
        elif e.kategoria == 'K':
            efekty_K.append({'symbol': f'EU_K{c_k:02d}', 'opis': e.opis, 'kod': e.kod, 'cele': cele_K,
                             'metoda': metody.get('K', '-')})
            c_k += 1

    tematy_db = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    tematy = []
    counters = {}
    for t in tematy_db:
        tresc, forma, efekty = t.temat, 'wykład', '-'
        if tresc.startswith('['):
            end_idx = tresc.find(']')
            if end_idx != -1:
                meta, tresc = tresc[1:end_idx], tresc[end_idx + 1:].strip()
                parts = [p.strip() for p in meta.split('|')]
                forma = parts[0]
                if len(parts) > 1 and parts[1]: efekty = parts[1]
        counters[forma] = counters.get(forma, 0) + 1
        tematy.append({'lp': counters[forma], 'tresc': tresc, 'efekty': efekty, 'forma': forma.capitalize()})

    context = {
        'przedmiot': przedmiot,
        'sylabus': sylabus,
        'cele_lista': cele_lista,
        'efekty_W': efekty_W,
        'efekty_U': efekty_U,
        'efekty_K': efekty_K,
        'tematy': tematy,
        'p_cw': p_cw, 'p_lab': p_lab, 'p_proj': p_proj, 'p_wyk': p_wyk, 'p_egz': p_egz, 'p_lit': p_lit,
        'h_egz': h_egz, 'sum_kon': sum_kon, 'sum_wla': sum_wla, 'sum_tot': sum_tot
    }

    html_string = render_to_string('core/sylabus_pdf.html', context)
    return HttpResponse(HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(),
                        content_type='application/pdf')


@login_required
def dodaj_wykladowce(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = WykladowcaUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save(commit=False)
        u.set_password(form.cleaned_data['password'])
        u.save()
        Wykladowca.objects.create(user=u, tytul=form.cleaned_data['tytul'], katedra=form.cleaned_data['katedra'])
        return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Dodaj Wykładowcę'})


@login_required
def dodaj_kierunek(request):
    if not request.user.is_superuser: return HttpResponseForbidden()
    form = KierunekForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_przedmiotow')
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Dodaj Kierunek'})


@login_required
def usun_przedmiot(request, przedmiot_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    # Usunięcie przedmiotu (dzięki on_delete=models.CASCADE w modelach,
    # system sam usunie też jego sylabus, tematy zajęć i historię czatu!)
    przedmiot.delete()

    return redirect('lista_przedmiotow')