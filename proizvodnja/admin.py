from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Dimenzija, Sestavina, Zaloga, Baza, Tip

admin.site.register(Zaloga)
admin.site.register(Dimenzija)
admin.site.register(Sestavina)
admin.site.register(Baza)
admin.site.register(Tip)
