from django.contrib import admin

from zaloga.models import Dnevna_prodaja,Stranka
from prodaja.models import Skupina

admin.site.register(Dnevna_prodaja)
admin.site.register(Stranka)
admin.site.register(Skupina)