from .models import Dnevna_prodaja, Zaloga, Sestavina, Baza, Sprememba, Cena
import json
from .models import Zaklep
from .models import TIPI_BAZE

dnevne_prodaje = Dnevna_prodaja.objects.all()[::-1]

def test_dnevna_prodaja(odDatum,doDatum):
    prodaje = dnevne_prodaje.filter(datum__lte = doDatum, datum__gte = odDatum)
    test_prodaje(prodaje)

def test_prodaje(prodaje):
    for prodaja in prodaje:
        print("delam " + str(prodaja.datum) + ":")
        for racun in prodaja.baza_set.all().filter(status="veljavno"):
            napacno = False
            for vnos in racun.vnos_set.all():
                if vnos.sprememba == None:
                   napacno = True
            if napacno:
                print("popravljam racun " + str(racun))
                cas = racun.cas
                racun.uveljavi_racun(racun.zaloga)
                racun.cas = cas
                racun.save()
        print("konec")

def popravi_racune(prodaje):
    for prodaja in prodaje:
        print("delam " + str(prodaja.datum) + ":")
        for racun in prodaja.baza_set.all().filter(status="veljavno"):
            racun.datum = prodaja.datum
            racun.save()
            for vnos in racun.vnos_set.all():
                vnos.save()

def dodaj_zaklep():
    zaklep = Zaklep.objects.all().first()
    prodajalna = Zaloga.objects.all()[1]
    zaklep_json = {}
    for sestavina in Sestavina.objects.all().filter(zaloga = prodajalna).iterator():
        zaklep_json[sestavina.pk] = {}
        for tip in prodajalna.vrni_tipe:
            zaklep_json[sestavina.pk][tip[0]] = getattr(sestavina,tip[0])
    Zaklep.objects.create(zaloga=prodajalna,datum=zaklep.datum,stanja_json = json.dumps(zaklep_json))

def popravi():
    baza1 = Baza.objects.get(title="PX-2020-6")
    baza2 = Baza.objects.get(title="PS-2020-6")
    baze = [baza1,baza2]
    for baza in baze:
        for vnos in baza.vnos_set.all():
            if vnos.dimenzija.dimenzija == "185/55/R14" and vnos.tip == "Y":
                tip = vnos.tip
                sestavina = Sestavina.objects.get(dimenzija = vnos.dimenzija, zaloga = baza.zaloga)
                vnos.delete()
                sestavina.nastavi_iz_sprememb(tip)
        baza.save()



def testiraj_baze():
    for zaloga in Zaloga.objects.all():
        testiraj_zalogo(zaloga)

def testiraj_zalogo(zaloga):
    for tip in TIPI_BAZE:
        testiraj_tip(zaloga,tip[0])

def testiraj_tip(zaloga,tip):
    for baza in Baza.objects.all().filter(zaloga = zaloga, tip = tip, status = "veljavno"):
        testiraj_bazo(baza)

def testiraj_bazo(baza):
    for vnos in baza.vnos_set.all():
        if vnos.sprememba == None:
            if baza.tip == "inventura":
                continue
            elif baza.tip == "racun":
                print("POPRAVLJAM RACUN")
            else:
                print(baza.zaloga.title + ";" + baza.title + ";" + vnos.dimenzija.dimenzija + ";" + vnos.tip + ";" + "sprememba ne obstaja")
                print("POPRAVLJAM")
                sestavina = Sestavina.objects.all().get(dimenzija = vnos.dimenzija, zaloga = baza.zaloga)
                sprememba = Sprememba.objects.all().filter(baza = baza, sestavina = sestavina).first()
                if sprememba == None:
                    print("SPREMEMBA NE OBSTAJA. USTVARJAM NOVO")
                    sprememba = Sprememba.objects.create(
                        sestavina = sestavina,
                        tip = vnos.tip,
                        stevilo = vnos.stevilo,
                        baza = baza)
                else:
                    print("SPREMEBA OBSTAJA VENDAR NI POD VNOSOM. POPRAVLJAM")
                vnos.sprememba = sprememba
                vnos.save()
        elif vnos.sprememba.tip != vnos.tip:
            print(baza.zaloga.title + ";" + baza.title + ";" + vnos.dimenzija.dimenzija + ";" + "napačen tip")

def testiraj_invenuro(baza):
    print("TESTIRAM INVENTURO")

def testiraj_stanja_zaklepov():
    for zaloga in Zaloga.objects.all():
        testiraj_stanje_zaklepa(zaloga)

def testiraj_stanje_zaklepa(zaloga):
    zaklep = zaloga.zaklep_zaloge
    stanja = zaklep.stanja
    for key in stanja:
        try:
            stanja_sestavine = stanja[key]
            for tip in zaloga.vrni_tipe:
                if tip[0] not in stanja_sestavine:
                    sestavina = Sestavina.objects.get(id = int(key))
                    print(tip[0] + " not in " + sestavina.dimenzija.dimenzija)
                    print("POPRAVLJAM")
                    stanja = zaklep.nastavi_stanje(sestavina,tip[0])
        except:
            print(key)
            print("NAPAČEN KEY")
            print("POPRAVLJAM")
            zaklep.remove_key(key)

    for sestavina in Sestavina.objects.all().filter(zaloga = zaloga):
        if str(sestavina.pk) not in stanja:
            print(sestavina.dimenzija.dimenzija + " NOT IN")
            print("POPRAVLJAM")
            for tip in zaloga.vrni_tipe:
                stanja = zaklep.nastavi_stanje(sestavina,tip[0])
    zaklep.save()
    zaloga.save()
                    
      