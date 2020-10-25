
import datetime
from zaloga.models import Dimenzija, Sestavina, Zaloga, Baza,Vnos

ZALOGA = 1


DIMENZIJA = 0
TIP = 1

PRVOTNI_TIP = 0
SPREMENJENI_TIP = 1

SPREMEMBE = [
    ["JP", "Y"],
    ["JP50","W"],
    ["JP70","W"]
]

IZJEME = [
    ["215/65/R16","JP70"],
    ["225/45/R18","JP70"]
]

datum = datetime.date.today()
title = "S-" + str(datum)
zaloga = Zaloga.objects.get(pk = ZALOGA)
tip = "inventura"

sestavine = Sestavina.objects.all().filter(zaloga = zaloga)

def je_izjema(dimenzija, tip):
    return [dimenzija,tip] in IZJEME

def ustvari_bazo_spremembe():
    baza = Baza.objects.create(
        title = title,
        tip = tip,
        datum = datum,
        zaloga = zaloga,
    )
    for sestavina in sestavine:
        for sprememba in SPREMEMBE:
            prvotni_tip = sprememba[PRVOTNI_TIP]
            spremenjeni_tip = sprememba[SPREMENJENI_TIP]
            if not je_izjema(sestavina.dimenzija.dimenzija,prvotni_tip):
                stevilo = getattr(sestavina,prvotni_tip)
                if stevilo > 0:
                    vnos = Vnos.objects.create(
                        dimenzija = sestavina.dimenzija,
                        tip = prvotni_tip,
                        stevilo = 0,
                        baza = baza
                    )
                    vnos = baza.vnos_set.all().filter(dimenzija = sestavina.dimenzija, tip = spremenjeni_tip).first()
                    if vnos == None:
                        vnos = Vnos.objects.create(
                            dimenzija = sestavina.dimenzija,
                            tip = spremenjeni_tip,
                            stevilo = getattr(sestavina,spremenjeni_tip) + stevilo,
                            baza = baza
                        )
                    else:
                        vnos.stevilo = vnos.stevilo + stevilo
                        vnos.save()
    baza.uveljavi(zaloga)

                    

            




