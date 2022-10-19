
from .models import *
from zaloga.models import Dimenzija as Dim

def initial():
    create_dimenzije()
    create_tipi()
    create_sestavine()

    podjetje = Podjetje.objects.create(
        naziv = "Semenic tire trading d.o.o."
    )
    print("CREATED: PODJETJE")

    ribce = PoslovnaEnota.objects.create(
        podjetje = podjetje,
        naziv = "PE Ribce"
    )
    print("CREATED: RIBCE")

    brezice = PoslovnaEnota.objects.create(
        podjetje = podjetje,
        naziv = "PE Dobova"
    )
    print("CREATED: DOBOVA")

    Zaloga.objects.create(
        naziv = "skladisce",
        poslovnaEnota = ribce
    )
    print("CREATED: SKLADISCE RIBCE")

    Zaloga.objects.create(
        naziv = "skladisce",
        poslovnaEnota = brezice
    )
    print("CREATED: SKLADISCE BREZICE")

def drop_all():
    Dimenzija.objects.all().delete()
    Tip.objects.all().delete()
    Sestavina.objects.all().delete()
    Podjetje.objects.all().delete()
    PoslovnaEnota.objects.all().delete()
    Zaloga.objects.all().delete()


def create_dimenzije():
    dimenzije = []
    for dim in Dim.objects.all().values():
        dimenzije.append(Dimenzija(
            radij = dim["radius"],
            sirina = dim["width"],
            visina = dim["height"],
            special = dim["special"],
            dimenzija = dim["dimenzija"]
        ))
    Dimenzija.objects.bulk_create(dimenzije)
    print("CREATED: DIMENZIJE")

def create_tipi():
    Tip.objects.create(
        naziv = "Yellow",
        kratica = "Y",
        barva = "yellow"
    )
    Tip.objects.create(
        naziv = "White",
        kratica = "W",
        barva = "white"
    )
    Tip.objects.create(
        naziv = "70%",
        kratica = "70%",
        barva = "red"
    )
    print("CREATED: TIPI")

def create_sestavine():
    sestavine = []
    
    sestavine.append(Sestavina(naziv = "Guma"))
    sestavine.append(Sestavina(naziv = "Guma R12-R16"))
    sestavine.append(Sestavina(naziv = "Guma R17-R20"))
    sestavine.append(Sestavina(naziv = "Guma R21-R24"))
    
    for dimenzija in Dimenzija.objects.all():
        sestavine.append(Sestavina(
            dimenzija = dimenzija,
            naziv = dimenzija.dimenzija
        ))
        for tip in Tip.objects.all():
            sestavine.append(Sestavina(
                dimenzija = dimenzija,
                tip = tip,
                naziv = dimenzija.dimenzija + "_" + tip.kratica
            ))
    Sestavina.objects.bulk_create(sestavine)
    print("CREATED: SESTAVINE")