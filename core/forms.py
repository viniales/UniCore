from django import forms
from .models import SzczegolySylabusa, Przedmiot, EfektKierunkowy

class SylabusForm(forms.ModelForm):
    jezyk_wykladowy = forms.CharField(max_length=50, required=False, label="Jzyk wykadowy")
    
    # CHECKBOXY
    efekty_kierunkowe = forms.ModelMultipleChoiceField(
        queryset=EfektKierunkowy.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Zaznacz realizowane efekty kierunkowe (z tabeli)"
    )

    harmonogram_raw = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control border-primary', 'rows': 5, 'placeholder': 'Wklej list tematów...'}),
        required=False, label="SMART PASTE"
    )

    class Meta:
        model = SzczegolySylabusa
        fields = [
            'opis_wstepny', 'wymagania_wstepne', 'efekty_wiedza', 'efekty_umiejetnosci', 'efekty_kompetencje',
            'mapowanie_efektow', 'metody_nauczania', 'formy_oceny', 'zasady_oceniania', 
            'odrabianie_zajec', 'wymagania_obecnosci', 'pw_przygotowanie_cw', 'pw_sprawozdania', 
            'pw_projekt', 'pw_wyklad', 'pw_egzamin', 'pw_literatura', 'literatura', 'inne_informacje'
        ]
        widgets = {
            field: forms.Textarea(attrs={'class': 'form-control', 'rows': 3}) for field in fields if 'pw_' not in field
        }

    def __init__(self, *args, **kwargs):
        super(SylabusForm, self).__init__(*args, **kwargs)
        for field in self.fields: self.fields[field].required = False
