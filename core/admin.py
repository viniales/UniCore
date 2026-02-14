from django.contrib import admin
from .models import *

class TrescZajecInline(admin.TabularInline):
    model = TrescZajec
    extra = 0

@admin.register(Wykladowca)
class WykladowcaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'get_firstname', 'get_lastname', 'get_username', 'katedra')
    def get_firstname(self, obj): return obj.user.first_name
    def get_lastname(self, obj): return obj.user.last_name
    def get_username(self, obj): return obj.user.username

@admin.register(Przedmiot)
class PrzedmiotAdmin(admin.ModelAdmin):
    list_display = ('nazwa_pl', 'kod_przedmiotu', 'ects')
    filter_horizontal = ('koordynatorzy',)
    inlines = [TrescZajecInline]

admin.site.register(EfektKierunkowy)
admin.site.register(KierunekStudiow)
admin.site.register(Modul)
admin.site.register(SzczegolySylabusa)
admin.site.register(TrescZajec)