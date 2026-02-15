from django.contrib import admin
from .models import *

class TrescZajecInline(admin.TabularInline):
    model = TrescZajec
    extra = 0

@admin.register(Przedmiot)
class PrzedmiotAdmin(admin.ModelAdmin):
    list_display = ("nazwa_pl", "kod_przedmiotu", "ects")
    # TUTAJ PRZYWRACAMY TWOJE OKIENKA:
    filter_horizontal = ("koordynatorzy", "efekty_kierunkowe")
    inlines = [TrescZajecInline]

admin.site.register(Wykladowca)
admin.site.register(EfektKierunkowy)
admin.site.register(KierunekStudiow)
admin.site.register(Modul)
admin.site.register(SzczegolySylabusa)
