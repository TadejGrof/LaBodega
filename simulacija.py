from zaloga.models import Zaloga,Dnevna_prodaja,Baza,Vnos,Sestavina,Sprememba,Cena,Kontejner
import datetime
from django.contrib.auth.models import User
from program.models import Program
from prodaja.models import Prodaja
import random

LETO = 2019
MESEC = 11
DAN = 28

ZACETEK = datetime.date(LETO,MESEC,DAN)
USER = User.objects.all().get(username="TadejGrof")

dan = ZACETEK
cas = datetime.datetime(LETO,MESEC,DAN,0,0,0)

program = Program.objects.all().first()
zaloga = Zaloga.objects.all().first()
prodaja = Prodaja.objects.all().first()

STRANKE = prodaja.stranka_set.all()

TIPI = zaloga.vrni_tipe
KRATKI_TIPI = [tip[0] for tip in TIPI]
DOLGI_TIPI = [tip[1] for tip in TIPI]
EVRPOSKI_TIPI = [ "Y", "W"]
JAPAN_TIPI = ["JP","JP50","JP70"]

def simulacija(stevilo_dni):
    print("delam zacetno inventuro")
    zacetna_inventura()
    for zaporedni_dan in range(stevilo_dni):
        print("delam " + str(zaporedni_dan + 1) + "/" + str(stevilo_dni))
        simulacija_dneva(zaporedni_dan)
        naslednji_dan()
    
def simulacija_dneva(dan_od_zacetka):
    #inventura:
    if dan_od_zacetka > 0 and dan_od_zacetka % 10 == 0:
        print("   delam inventuro")
        inventura()
    #odpis:
    if dan_od_zacetka > 0 and dan_od_zacetka % 20 == 0:
        print("   delam odpis")
        odpis()
    #prevzem_evropa
    if dan_od_zacetka > 0 and dan_od_zacetka % 7 == 0:
        print("   delam prevzem evropa")
        prevzem_evropa()
    if dan_od_zacetka > 0 and dan_od_zacetka % 3 == 0:
        print("   delam prevzem japan")
        prevzem_japonska()
    print("   delam dnevno prodajo")
    dnevna_prodaja()
    print("   delam prodaje")
    prodaja()

def zacetna_inventura():
    inventura = Baza.objects.create(
        tip="inventura",
        title= program.naslednja_inventura(True),
        datum = dan,
        author = USER)
    vnosi = []
    for sestavina in zaloga.sestavina_set.all().values():
        for tip in KRATKI_TIPI:
            stevilo = random.randint(0,10)
            if stevilo > 8:
                stevilo = random.randint(0,120)
            elif stevilo > 5:
                stevilo = random.randint(0,60)
            elif stevilo > 2:
                stevilo = random.randint(0,10)
            else:
                stevilo = 0
            vnosi.append(Vnos(dimenzija_id = sestavina['dimenzija_id'], tip = tip, stevilo = stevilo,baza = inventura))
    Vnos.objects.bulk_create(vnosi)
    inventura.uveljavi_inventuro(dan,cas)
    dodaj_cas()

def inventura():
    inventura = Baza.objects.create(
        tip="inventura",
        title=program.naslednja_inventura(True),
        datum = dan,
        author = USER)
    vnosi = []
    for sestavina in zaloga.sestavina_set.all().values():
        for tip in KRATKI_TIPI:
            stevilo = sestavina[tip]
            if stevilo < 0:
                razlika = - stevilo
            elif stevilo < 3:
                razlika = 0
            else:
                razlika = random.choice([-2,-2,-1,-1,-1,1,1,1,2,2] + [0 for _ in range(20)])
            stevilo += razlika    
            vnosi.append(Vnos(baza=inventura,stevilo=stevilo,tip=tip,dimenzija_id=sestavina['dimenzija_id']))
    Vnos.objects.bulk_create(vnosi)
    inventura.uveljavi_inventuro(dan,cas)
    dodaj_cas()

def odpis():
    baza = Baza.objects.create(
        tip="odpis",
        title=program.naslednji_odpis(True),
        datum = dan,
        author = USER)
    vnosi = []
    for sestavina in zaloga.sestavina_set.all().values():
        for tip in KRATKI_TIPI:
            stevilo = sestavina[tip]
            odpis = (stevilo * 3) // 100
            if odpis > 0:
                vnosi.append(Vnos(baza=baza,stevilo=odpis,tip=tip,dimenzija_id=sestavina['dimenzija_id']))
    Vnos.objects.bulk_create(vnosi)
    baza.uveljavi(dan,cas)
    dodaj_cas()

def dnevna_prodaja():
    prodaja = Dnevna_prodaja.objects.create(datum = dan)
    prodaja.doloci_title()
    stevilo_racunov = random.randint(30,40)
    sestavine = zaloga.sestavina_set.all().filter(W__gte = 1).values('W','dimenzija_id','id')
    stevilo = 0
    while stevilo < stevilo_racunov:
        sestavina = random.choice(sestavine)
        nakup = random.choice([1 for _ in range(15)] + [2 for _ in range(10)] + [3 for _ in range(3)] + [4 for _ in range(5)])
        while nakup > sestavina["W"]:
            nakup -= 1
        racun = Baza.objects.create(
            title= program.naslednji_racun(delaj=True),
            tip='racun',
            dnevna_prodaja = prodaja,
            popust = 0,
            author=USER)
        cena = Cena.objects.get(
            sestavina_id=sestavina['id'],
            tip="W",
            prodaja="dnevna_prodaja").cena
        Vnos.objects.create(
            baza = racun,
            stevilo= nakup,
            tip="W",
            cena = cena,
            dimenzija_id=sestavina['dimenzija_id'])
        racun.uveljavi_racun()
        stevilo += 1
    dodaj_cas()

def prevzem_japonska():
    kontejner = Kontejner.objects.create(stevilka="JP",posiljatelj="Bozo",drzava="Japan")
    baza = Baza.objects.create(
        datum = dan,
        title = program.naslednji_prevzem(True),
        author = USER,
        kontejner = kontejner,
        tip = "prevzem",
        sprememba_zaloge = 1)
    skupno_stevilo = random.randint(1600,1900)
    sestavine = zaloga.sestavina_set.all().values("JP","JP50","JP70","dimenzija_id")
    vnosi = []
    stevilo = 0
    while stevilo < skupno_stevilo:
        sestavina = random.choice(sestavine)
        tip = random.choice(JAPAN_TIPI)
        if sestavina[tip] < 20:
            kolicina = random.randint(1,60)
        elif sestavina[tip] < 50:
            kolicina = random.randint(1,10)
        else:
            continue
        while stevilo + kolicina > skupno_stevilo:
            kolicina -= 1
        vnosi.append(Vnos(baza=baza,stevilo=kolicina,tip=tip,dimenzija_id=sestavina["dimenzija_id"]))
        stevilo += kolicina
    Vnos.objects.bulk_create(vnosi)
    baza.uveljavi(dan,cas)
    dodaj_cas()

def prevzem_evropa():
    kontejner = Kontejner.objects.create(stevilka="EU",posiljatelj="Bozo",drzava="Slovenia")
    baza = Baza.objects.create(
        datum = dan,
        title = program.naslednji_prevzem(True),
        author = USER,
        kontejner = kontejner,
        tip = "prevzem",
        sprememba_zaloge = 1)
    skupno_stevilo = random.randint(2900,3100)
    sestavine = zaloga.sestavina_set.all().values("Y","W","id","dimenzija_id")
    vnosi = []
    stevilo = 0
    while stevilo < skupno_stevilo:
        sestavina = random.choice(sestavine)
        tip = random.choice(EVRPOSKI_TIPI)
        if sestavina[tip] < 20:
            kolicina = random.randint(1,60)
        elif sestavina[tip] < 50:
            kolicina = random.randint(1,10)
        else:
            continue
        while stevilo + kolicina > skupno_stevilo:
            kolicina -= 1
        vnosi.append(Vnos(baza=baza,stevilo=kolicina,tip=tip,dimenzija_id=sestavina["dimenzija_id"]))
        stevilo += kolicina
    Vnos.objects.bulk_create(vnosi)
    baza.uveljavi(dan,cas)
    dodaj_cas()

def prodaja():
    stevilo_prodaj = random.randint(3,6)
    for n in range(stevilo_prodaj):
        print("      " + str(n+1) + "/" + str(stevilo_prodaj))
        stranka = random.choice(STRANKE)
        baza = Baza.objects.create(
            tip = "vele_prodaja",
            stranka = stranka,
            datum = dan,
            title = program.naslednja_faktura(True),
            author = USER,
            popust = 0)
        skupno_stevilo = random.randint(200,400)
        stevilo = 0
        sestavine = zaloga.sestavina_set.all().values()
        vnosi = []
        while stevilo < skupno_stevilo:
            sestavina = random.choice(sestavine)
            tip = random.choice(KRATKI_TIPI)
            if sestavina[tip] <= 0:
                continue
            elif sestavina[tip] < 20:
                kolicina = random.randint(1,5 if sestavina[tip] > 4 else sestavina[tip])
            elif sestavina[tip] < 50:
                kolicina = random.randint(5,15)
            else:
                kolicina = random.randint(10,25)
            while stevilo + kolicina > skupno_stevilo:
                kolicina -= 1
            cena = Cena.objects.get(sestavina_id=sestavina['id'],tip=tip,prodaja="vele_prodaja").cena
            vnosi.append(Vnos(
                baza=baza,
                stevilo=kolicina,
                tip=tip,
                cena = cena,
                dimenzija_id=sestavina["dimenzija_id"]))
            stevilo += kolicina
        Vnos.objects.bulk_create(vnosi)
        baza.uveljavi(dan,cas)
        dodaj_cas()

##############################################################
def dodaj_cas():
    global cas
    cas = cas + datetime.timedelta(seconds=1)

def naslednji_dan():
    global dan
    dan = dan + datetime.timedelta(days=1)
    global cas
    cas = datetime.datetime(dan.year,dan.month,dan.day,0,0,0)

