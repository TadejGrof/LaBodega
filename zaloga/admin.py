from django.contrib import admin
from .models import Dimenzija, Sestavina, Zaloga, Vnos,Baza, Stroski_Group, Kontejner

admin.site.register(Zaloga)
admin.site.register(Dimenzija)
admin.site.register(Sestavina)
admin.site.register(Baza)
admin.site.register(Vnos)
admin.site.register(Stroski_Group)
admin.site.register(Kontejner)
