from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from .models import Przedmiot, SzczegolySylabusa, TrescZajec, KierunekStudiow, Modul, EfektKierunkowy, Wykladowca
from .forms import SylabusForm, PrzedmiotForm, WykladowcaUserForm, KierunekForm
import re


@login_required
def lista_przedmiotow(request):
    wykladowca = getattr(request.user, 'wykladowca', None)

    if request.user.is_superuser:
        return render(request, 'core/panel_zarzadzania.html', {
            'przedmioty': Przedmiot.objects.all(),
            'kierunki': KierunekStudiow.objects.all(),
            'tryb': 'Prodziekan'
        })

    if wykladowca:
        kierunki_pod_opieka = KierunekStudiow.objects.filter(koordynator=wykladowca)
        przedmioty_kierunku = Przedmiot.objects.filter(modul__kierunek__in=kierunki_pod_opieka)
        moje_prowadzone = Przedmiot.objects.filter(koordynatorzy=wykladowca)  # Poprawiona nazwa

        wszystkie_widoczne = (przedmioty_kierunku | moje_prowadzone).distinct()

        return render(request, 'core/panel_zarzadzania.html', {
            'przedmioty': wszystkie_widoczne,
            'przedmioty_kierunku_ids': list(przedmioty_kierunku.values_list('id', flat=True)),
            'moje_przedmioty_ids': list(moje_prowadzone.values_list('id', flat=True)),
            'tryb': 'Panel Wykładowcy / Koordynatora'
        })

    return HttpResponse("Błąd: Twoje konto nie posiada przypisanego profilu Wykładowcy.")


@login_required
def zarzadzaj_przedmiotem(request, przedmiot_id=None):
    wykladowca = getattr(request.user, 'wykladowca', None)
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id) if przedmiot_id else None
    is_dean = request.user.is_superuser

    if not is_dean:
        if not przedmiot or przedmiot.modul.kierunek.koordynator != wykladowca:
            return HttpResponseForbidden("Brak uprawnień do tego przedmiotu.")

    if request.method == 'POST':
        form = PrzedmiotForm(request.POST, instance=przedmiot)
        if form.is_valid():
            p = form.save(commit=False)

            # Pobieramy dane z formularza
            k = form.cleaned_data['kierunek']
            s = form.cleaned_data['semestr']
            t = form.cleaned_data['typ_zajec']

            modul, _ = Modul.objects.get_or_create(
                kierunek=k, semestr=s, typ=t,
                defaults={
                    'kod_modulu': f"{k.nazwa[:3].upper()}-{s}-{t[:3].upper()}",
                    'nazwa': f"{t} - Semestr {s}",
                    'wymagane_ects': 30
                }
            )

            p.modul = modul
            p.save()
            form.save_m2m()  # Zapisujemy koordynatorów i efekty

            # Efekty kierunkowe
            usun = request.POST.getlist('usun_efekt')
            if usun: p.efekty_kierunkowe.filter(id__in=usun).delete()

            katy = request.POST.getlist('nowy_efekt_kat')
            opisy = request.POST.getlist('nowy_efekt_opis')

            for kt, op in zip(katy, opisy):
                if op.strip():
                    max_num = 0
                    for e in p.efekty_kierunkowe.filter(kategoria=kt):
                        match = re.search(r'(\d+)$', e.kod)
                        if match: max_num = max(max_num, int(match.group(1)))
                    ne = EfektKierunkowy.objects.create(kod=f"K_{kt}{max_num + 1:02d}", kategoria=kt, opis=op.strip())
                    p.efekty_kierunkowe.add(ne)

            return redirect('zarzadzaj_przedmiotem', przedmiot_id=p.id)
    else:
        # KLUCZOWY FIX: Przekazujemy aktualne dane modułu do pól formularza
        initial_data = {}
        if przedmiot and przedmiot.modul:
            initial_data = {
                'kierunek': przedmiot.modul.kierunek,
                'semestr': przedmiot.modul.semestr,
                'typ_zajec': przedmiot.modul.typ,
            }
        form = PrzedmiotForm(instance=przedmiot, initial=initial_data)

    return render(request, 'core/formularz_przedmiotu.html', {
        'form': form,
        'przedmiot': przedmiot,
        'is_dean': is_dean
    })


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
            if wybrane is not None: przedmiot.efekty_kierunkowe.set(wybrane)

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
        form = SylabusForm(instance=sylabus, initial={"efekty_kierunkowe": przedmiot.efekty_kierunkowe.all(),
                                                      "harmonogram_raw": harmonogram_text})
        form.fields["efekty_kierunkowe"].queryset = przedmiot.efekty_kierunkowe.all()

    tematy_db = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    tematy_zdekodowane = []
    counters = {}
    for t in tematy_db:
        tresc, forma, efekty = t.temat, 'wykład', ''
        if tresc.startswith('['):
            end_idx = tresc.find(']')
            if end_idx != -1:
                meta = tresc[1:end_idx]
                tresc = tresc[end_idx + 1:].strip()
                parts = meta.split('|')
                forma = parts[0].strip()
                if len(parts) > 1: efekty = parts[1].strip()
        counters[forma] = counters.get(forma, 0) + 1
        tematy_zdekodowane.append({'lp': counters[forma], 'tresc': tresc, 'efekty': efekty, 'forma': forma})

    return render(request, 'core/edycja_sylabusa.html',
                  {'form': form, 'przedmiot': przedmiot, 'tematy': tematy_zdekodowane})


@login_required
def grid_kierunku(request, kierunek_id):
    kierunek = get_object_or_404(KierunekStudiow, id=kierunek_id)
    return HttpResponse(f"Grid dla {kierunek.nazwa}")


@login_required
def pobierz_pdf(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    sylabus, _ = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)
    html_string = render_to_string('core/sylabus_pdf.html', {'przedmiot': przedmiot, 'sylabus': sylabus})
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
    return render(request, 'core/formularz_uniwersalny.html', {'form': form, 'tytul': 'Dodaj Kierunek Studiów'})