from django.test import TestCase

from .models import Zaloga, Sestavina, Dimenzija, Zaklep


def preveriZaklepZaloge():
    for zaloga in Zaloga.objects.all():
        zaklep = zaloga.zaklep_zaloge
        stanja = zaklep.stanja
        for sestavina in zaloga.sestavina_set.all():
            if str(sestavina.pk) not in stanja:
                print(sestavina.dimenzija.dimenzija)

def preveriInNastaviZaklepZaloge():
    for zaloga in Zaloga.objects.all():
        zaklep = zaloga.zaklep_zaloge
        stanja = zaklep.stanja
        for sestavina in zaloga.sestavina_set.all():
            if str(sestavina.pk) not in stanja:
                for tip in zaloga.vrni_tipe:
                    zaklep.nastavi_stanje(sestavina,tip[0])
