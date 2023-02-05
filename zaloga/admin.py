from django.contrib import admin
from .models import Zaklep,Dimenzija, Sestavina, Zaloga, Vnos,Baza, Stroski_Group, Kontejner
from .models import TIPI_BAZE

admin.site.register(Zaloga)

admin.site.register(Sestavina)

class TipListFilter(admin.SimpleListFilter):
    title = ('tip baze')
    parameter_name = 'tip'

    def lookups(self, request, model_admin):
        return TIPI_BAZE

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        else:
            return queryset.filter(tip = self.value())

@admin.register(Baza)
class BazaAdmin(admin.ModelAdmin):
    list_display = ('title','status','zaloga', 'tip', 'datum','stranka','kontejner','dnevna_prodaja','zalogaPrenosa')
    list_filter = (TipListFilter,"zaloga","stranka",)

@admin.register(Dimenzija)
class BazaAdmin(admin.ModelAdmin):
    list_display = ('dimenzija', 'radius', 'height', 'width', 'special', 'diameter')


admin.site.register(Zaklep)
admin.site.register(Vnos)
admin.site.register(Stroski_Group)
admin.site.register(Kontejner)
