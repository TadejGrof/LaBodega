from django.test import TestCase

from program.models import Drzava
from .models import Zaloga, Sestavina, Dimenzija, Zaklep, Dobavitelj, Baza
import datetime

def nastavi_datume_uveljavitev():
    for baza in Baza.objects.all().filter(status="veljavno"):
        cas = None
        datum = None
        if baza.tip == "racun":
            try:
                cas = baza.cas
                datum = baza.dnevna_prodaja.datum
            except:
                continue
        if cas == None:
            cas = datetime.datetime.now().time()
        if datum == None:
            datum = baza.datum
        cas_uveljavitve = datetime.datetime.combine(datum,cas)
        baza.cas_uveljavitve = cas_uveljavitve
        baza.save()
        
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

