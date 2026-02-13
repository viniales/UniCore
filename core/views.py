from django.shortcuts import render, get_object_or_404, redirect
from .models import Modul, Przedmiot, SzczegolySylabusa, TrescZajec
from .forms import SylabusForm

def widok_niebieski(request):
    moduly = Modul.objects.prefetch_related('przedmioty').all().order_by('semestr', 'id')
    return render(request, 'core/widok_niebieski.html', {'moduly': moduly})

def edycja_sylabusa(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    szczegoly, created = SzczegolySylabusa.objects.get_or_create(przedmiot=przedmiot)
    tematy = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')

    if request.method == 'POST':
        form = SylabusForm(request.POST, instance=szczegoly)
        if form.is_valid():
            obj = form.save(commit=False)
            # Zapisz jezyk bezposrednio w przedmiocie
            przedmiot.jezyk_wykladowy = form.cleaned_data.get('jezyk_wykladowy')
            przedmiot.save()
            
            # Naprawa pustych pol liczbowych (zamiana None na 0)
            for f in ['pw_przygotowanie_cw', 'pw_sprawozdania', 'pw_projekt', 'pw_wyklad', 'pw_egzamin', 'pw_literatura']:
                setattr(obj, f, getattr(obj, f) or 0)
            obj.save()
            
            # Smart Paste (Harmonogram)
            raw_text = form.cleaned_data.get('harmonogram_raw')
            if raw_text:
                TrescZajec.objects.filter(przedmiot=przedmiot).delete()
                for i, linia in enumerate(raw_text.splitlines(), 1):
                    if linia.strip():
                        TrescZajec.objects.create(przedmiot=przedmiot, numer_tematu=i, temat=linia.strip(), liczba_godzin=2)
            
            return redirect('widok_niebieski')
    else:
        form = SylabusForm(instance=szczegoly, initial={'jezyk_wykladowy': przedmiot.jezyk_wykladowy})

    return render(request, 'core/edycja_sylabusa.html', {'form': form, 'przedmiot': przedmiot, 'tematy': tematy})

def sylabus_pdf(request, przedmiot_id):
    przedmiot = get_object_or_404(Przedmiot, id=przedmiot_id)
    szczegoly = get_object_or_404(SzczegolySylabusa, przedmiot=przedmiot)
    tematy = TrescZajec.objects.filter(przedmiot=przedmiot).order_by('numer_tematu')
    
    # Bezpieczne sumowanie godzin
    def s(val): return val if val else 0
    
    s_kontakt = s(przedmiot.godz_wyklad) + s(przedmiot.godz_cwiczenia) + s(przedmiot.godz_lab) + \
                s(przedmiot.godz_projekt) + s(przedmiot.godz_seminarium) + s(przedmiot.godz_egzamin)
    
    s_wlasna = s(szczegoly.pw_przygotowanie_cw) + s(szczegoly.pw_sprawozdania) + \
               s(szczegoly.pw_projekt) + s(szczegoly.pw_wyklad) + \
               s(szczegoly.pw_egzamin) + s(szczegoly.pw_literatura)

    return render(request, 'core/sylabus_pdf.html', {
        'przedmiot': przedmiot, 'szczegoly': szczegoly, 'tematy': tematy,
        'suma_kontaktowe': s_kontakt, 'suma_wlasna': s_wlasna, 'suma_calkowita': s_kontakt + s_wlasna
    })