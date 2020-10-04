from .models import Dnevna_prodaja, Zaloga, Sestavina, Baza, Sprememba, Cena
import json
from .models import Zaklep

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
    baza1 = Baza.objects.get(title="PX-2020-4")
    baza2 = Baza.objects.get(title="PS-2020-4")
    baze = [baza1,baza2]
    for baza in baze:
        for vnos in baza.vnos_set.all():
            if vnos.dimenzija.dimenzija == "205/60/R16" and vnos.tip == "Y":
                tip = vnos.tip
                sestavina = Sestavina.objects.get(dimenzija = vnos.dimenzija, zaloga = baza.zaloga)
                vnos.delete()
                sestavina.nastavi_iz_sprememb(tip)
        baza.save()


