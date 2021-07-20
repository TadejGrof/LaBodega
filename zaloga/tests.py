from django.test import TestCase

from program.models import Drzava
from .models import Zaloga, Sestavina, Dimenzija, Zaklep, Dobavitelj, Baza

def nastavi_dobavitelje():
    prevzemi = Baza.objects.all().filter(tip="prevzem")
    for prevzem in prevzemi:
        if prevzem.kontejner != None:
            upper = prevzem.kontejner.drzava.upper()
            try:
                drzava = Drzava.objects.get(kratica=upper)
            except:
                print(upper)
                drazava = Drzava.objects.get(kratica="SLO")
            try:
                dobavitelj = Dobavitelj.objects.get(podjetje__drzava=drzava)
                prevzem.dobavitelj = dobavitelj
                prevzem.save()
            except:
                print("NAPAKA")

