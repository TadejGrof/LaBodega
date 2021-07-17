from django.contrib import admin

from program.models import Program
from program.models import Profil, Drzava, Oseba

admin.site.register(Program)
admin.site.register(Profil)
admin.site.register(Drzava)
admin.site.register(Oseba)

# Register your models here.
