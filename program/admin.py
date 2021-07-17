from django.contrib import admin

from program.models import Program
from program.models import Profil, Drzava, Oseba, Podjetje

admin.site.register(Program)
admin.site.register(Profil)
admin.site.register(Drzava)
admin.site.register(Oseba)
admin.site.register(Podjetje)
# Register your models here.
