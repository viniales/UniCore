from django import forms
from django.contrib.auth.models import User
from .models import SzczegolySylabusa, Przedmiot, EfektKierunkowy, Wykladowca, Modul, KierunekStudiow

class SylabusForm(forms.ModelForm):
    efekty_kierunkowe = forms.ModelMultipleChoiceField(queryset=EfektKierunkowy.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    harmonogram_raw = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control border-primary shadow-sm', 'rows': 5}), required=False)
    class Meta:
        model = SzczegolySylabusa
        exclude = ['przedmiot', 'inne_informacje']
        widgets = {
            'wymagania_wstepne': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'metody_nauczania': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'formy_oceny': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'zasady_oceniania': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'odrabianie_zajec': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'wymagania_obecnosci': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'literatura': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields: self.fields[field].required = False

class PrzedmiotForm(forms.ModelForm):
    kierunek = forms.ModelChoiceField(queryset=KierunekStudiow.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    typ_zajec = forms.ChoiceField(choices=Modul.TYPY, widget=forms.Select(attrs={'class': 'form-select'}))
    semestr = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Przedmiot
        fields = ['status', 'nazwa_pl', 'nazwa_en', 'kod_przedmiotu', 'ects', 'jezyk_wykladowy', 'cykl_dydaktyczny',
                  'badania_naukowe', 'godz_wyklad', 'godz_cwiczenia', 'godz_lab', 'godz_projekt', 'godz_seminarium',
                  'godz_egzamin', 'koordynatorzy']
        widgets = {
            'koordynatorzy': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-select border-primary shadow-sm fw-bold'}),
        }

class KierunekForm(forms.ModelForm):
    class Meta:
        model = KierunekStudiow
        fields = '__all__'

class WykladowcaUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    tytul = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    katedra = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']