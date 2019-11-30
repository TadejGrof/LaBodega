from django.contrib import admin
from .models import Dimenzija, Sestavina, Zaloga, Vnos,Baza

admin.site.register(Zaloga)
admin.site.register(Dimenzija)
admin.site.register(Sestavina)
admin.site.register(Baza)
admin.site.register(Vnos)
