from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from .models import Przedmiot, SzczegolySylabusa, TrescZajec
from .forms import SylabusForm


def lista_przedmiotow(request):
    przedmioty = Przedmiot.objects.all()
    return render(request, 'core/lista.html', {'przedmioty': przedmioty})


def edycja_sylabusa(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    sylabus, created = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)
    if request.method == 'POST':
        form = SylabusForm(request.POST, instance=sylabus)
        if form.is_valid():
            form.save()
            wybrane = form.cleaned_data.get('efekty_kierunkowe')
            if wybrane is not None:
                przedmiot.efekty_kierunkowe.set(wybrane)
            raw = form.cleaned_data.get('harmonogram_raw')
            if raw:
                TrescZajec.objects.filter(przedmiot=przedmiot).delete()
                for i, line in enumerate(raw.strip().split('\n'), 1):
                    if line.strip():
                        TrescZajec.objects.create(przedmiot=przedmiot, numer_tematu=i, temat=line.strip(),
                                                  liczba_godzin=2)
            return redirect('edycja_sylabusa', przedmiot_id=przedmiot.id)
    else:
        form = SylabusForm(instance=sylabus, initial={'efekty_kierunkowe': przedmiot.efekty_kierunkowe.all()})
    tematy = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    return render(request, 'core/edycja_sylabusa.html', {'form': form, 'przedmiot': przedmiot, 'tematy': tematy})


def pobierz_pdf(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    sylabus, _ = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)
    tematy = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')

    # DEKODOWANIE CELÓW I METOD PODZIELONYCH NA W, U, K
    raw_text = sylabus.opis_wstepny or ""
    cele_lista = []
    metody_dict = {}
    mode = 'cele'

    for line in raw_text.split('\n'):
        line = line.strip()
        if not line: continue
        if line == '---METODY---':
            mode = 'metody'
            continue

        parts = line.split('|')
        if mode == 'cele' and len(parts) >= 3:
            cele_lista.append({
                'kategoria': parts[0].strip(),
                'kod': parts[1].strip(),
                'tresc': parts[2].strip()
            })
        elif mode == 'metody' and len(parts) >= 2:
            metody_dict[parts[0].strip()] = parts[1].strip()

    # FUNKCJA PRZYPISUJĄCA WŁAŚCIWE CELE I METODY DO W, U, K
    def przygotuj_efekty(queryset, kategoria):
        wynik = []
        # Szukamy celów O1, O2 tylko dla tej kategorii
        przypisane_cele = [c['kod'] for c in cele_lista if c['kategoria'] == kategoria]
        cele_string = ", ".join(przypisane_cele)
        metoda = metody_dict.get(kategoria, sylabus.formy_oceny or "")

        for i, efekt in enumerate(queryset, 1):
            wynik.append({
                'symbol': f"{kategoria}{i}",
                'opis': efekt.opis,
                'kod': efekt.kod,
                'cele': cele_string,
                'metoda': metoda
            })
        return wynik

    efekty_W = przygotuj_efekty(przedmiot.efekty_kierunkowe.filter(kategoria='W'), 'W')
    efekty_U = przygotuj_efekty(przedmiot.efekty_kierunkowe.filter(kategoria='U'), 'U')
    efekty_K = przygotuj_efekty(przedmiot.efekty_kierunkowe.filter(kategoria='K'), 'K')

    # Obliczenia godzin pracy studenta
    h_wyk = przedmiot.godz_wyklad or 0
    h_cw = przedmiot.godz_cwiczenia or 0
    h_lab = przedmiot.godz_lab or 0
    h_proj = przedmiot.godz_projekt or 0
    h_sem = przedmiot.godz_seminarium or 0
    h_egz = 2 if sylabus.pw_egzamin else 0
    sum_kon = h_wyk + h_cw + h_lab + h_proj + h_sem + h_egz

    p_cw = sylabus.pw_przygotowanie_cw or 0
    p_lab = sylabus.pw_sprawozdania or 0
    p_proj = sylabus.pw_projekt or 0
    p_wyk = sylabus.pw_wyklad or 0
    p_egz = sylabus.pw_egzamin or 0
    p_lit = sylabus.pw_literatura or 0
    sum_wla = p_cw + p_lab + p_proj + p_wyk + p_egz + p_lit

    context = {
        'przedmiot': przedmiot, 'sylabus': sylabus, 'tematy': tematy,
        'cele_lista': cele_lista,
        'efekty_W': efekty_W, 'efekty_U': efekty_U, 'efekty_K': efekty_K,
        'sum_kon': sum_kon, 'sum_wla': sum_wla, 'sum_tot': sum_kon + sum_wla,
        'h_egz': h_egz, 'p_cw': p_cw, 'p_lab': p_lab, 'p_proj': p_proj,
        'p_wyk': p_wyk, 'p_egz': p_egz, 'p_lit': p_lit
    }

    # Renderowanie HTML
    html_string = render_to_string('core/sylabus_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Sylabus_{przedmiot.kod_przedmiotu}.pdf"'
    return response